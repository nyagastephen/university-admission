import os
import uuid
from flask import send_file
from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import current_app
from flask_login import login_required
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.applicant_profile import ApplicantProfile
from app.models.uploaded_document import UploadedDocument
import mimetypes
from flask import jsonify
from flask import url_for

document = Blueprint("document", __name__)


DOCUMENT_TYPES = [

    "Passport Photo",

    "National ID",

    "Birth Certificate",

    "KCSE Certificate",

    "KCSE Result Slip"

]


ALLOWED_EXTENSIONS = {

    "pdf",

    "jpg",

    "jpeg",

    "png"

}


def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(".", 1)[1].lower()

        in ALLOWED_EXTENSIONS

    )


def get_profile():

    return ApplicantProfile.query.filter_by(

        user_id=current_user.id

    ).first()


def upload_folder(profile):

    folder = os.path.join(

        current_app.config["UPLOAD_FOLDER"],

        "applicants",

        str(profile.id)

    )

    os.makedirs(folder, exist_ok=True)

    return folder


@document.route("/documents")
@login_required
def list_documents():

    profile = get_profile()

    uploaded = {

        d.document_type: d

        for d in UploadedDocument.query.filter_by(

            applicant_profile_id=profile.id

        ).all()

    }

    uploaded_count = len(uploaded)

    required_count = len(DOCUMENT_TYPES)

    documents_complete = (

        uploaded_count == required_count

    )

    return render_template(

        "documents/list.html",

        document_types=DOCUMENT_TYPES,

        uploaded=uploaded,

        uploaded_count=uploaded_count,

        required_count=required_count,

        documents_complete=documents_complete

    )


@document.route("/documents/upload/<document_type>", methods=["GET", "POST"])
@login_required
def upload_document(document_type):

    if document_type not in DOCUMENT_TYPES:

        flash(

            "Invalid document type.",

            "danger"

        )

        return redirect(

            url_for("document.list_documents")

        )

    profile = get_profile()

    existing = UploadedDocument.query.filter_by(

        applicant_profile_id=profile.id,

        document_type=document_type

    ).first()

    if request.method == "POST":

        file = request.files.get("document")

        if file is None or file.filename == "":

            flash(

                "Please choose a file.",

                "danger"

            )

            return redirect(request.url)

        if not allowed_file(file.filename):

            flash(

                "Only PDF, JPG, JPEG and PNG files are allowed.",

                "danger"

            )

            return redirect(request.url)

        filename = secure_filename(file.filename)

        extension = filename.rsplit(".", 1)[1].lower()

        stored_filename = f"{uuid.uuid4()}.{extension}"

        folder = upload_folder(profile)

        path = os.path.join(

            folder,

            stored_filename

        )

        file.save(path)

        if existing:

            flash(

                f"{document_type} already exists.",

                "warning"

            )

            return render_template(

                "documents/replace.html",

                existing=existing,

                document_type=document_type,

                new_filename=filename,

                new_stored_filename=stored_filename

            )

        document_record = UploadedDocument(

            applicant_profile_id=profile.id,

            document_type=document_type,

            original_filename=filename,

            stored_filename=stored_filename

        )

        db.session.add(document_record)

        db.session.commit()

        flash(

            "Document uploaded successfully.",

            "success"

        )

        return redirect(

            url_for("document.list_documents")

        )

    return render_template(

        "documents/upload.html",

        document_type=document_type

    )


@document.route("/documents/<int:id>/replace", methods=["POST"])
@login_required
def replace_document(id):

    profile = get_profile()

    document_record = UploadedDocument.query.get_or_404(id)

    if document_record.applicant_profile_id != profile.id:

        flash(

            "Access denied.",

            "danger"

        )

        return redirect(

            url_for("document.list_documents")

        )

    file = request.files.get("document")

    if file is None or file.filename == "":

        flash(

            "Please choose a file.",

            "danger"

        )

        return redirect(

            url_for("document.list_documents")

        )

    if not allowed_file(file.filename):

        flash(

            "Invalid file type.",

            "danger"

        )

        return redirect(

            url_for("document.list_documents")

        )

    filename = secure_filename(file.filename)

    extension = filename.rsplit(".", 1)[1].lower()

    stored_filename = f"{uuid.uuid4()}.{extension}"

    folder = upload_folder(profile)

    old_path = os.path.join(

        folder,

        document_record.stored_filename

    )

    if os.path.exists(old_path):

        os.remove(old_path)

    file.save(

        os.path.join(

            folder,

            stored_filename

        )

    )

    document_record.original_filename = filename

    document_record.stored_filename = stored_filename

    db.session.commit()

    flash(

        "Document replaced successfully.",

        "success"

    )

    return redirect(

        url_for("document.list_documents")

    )
@document.route("/documents/<int:id>/preview")
@login_required
def preview_document(id):

    document = UploadedDocument.query.get_or_404(id)

    profile = ApplicantProfile.query.get(
        document.applicant_profile_id
    )

    # Applicants can only preview their own documents.
    if current_user.role == "Applicant":

        applicant = get_profile()

        if (
            applicant is None or
            applicant.id != profile.id
        ):
            abort(403)

    # Admissions Officers and Admins may preview any document.

    folder = upload_folder(profile)

    path = os.path.join(
        folder,
        document.stored_filename
    )

    return send_file(path)

@document.route("/documents/<int:id>/info")
@login_required
def document_info(id):

    document = UploadedDocument.query.get_or_404(id)

    profile = ApplicantProfile.query.get(
        document.applicant_profile_id
    )

    if current_user.role == "Applicant":

        applicant = get_profile()

        if applicant.id != profile.id:
            abort(403)

    extension = document.original_filename.rsplit(".", 1)[1].lower()

    return jsonify({

        "url": url_for(
            "document.preview_document",
            id=document.id
        ),

        "extension": extension,

        "filename": document.original_filename

    })