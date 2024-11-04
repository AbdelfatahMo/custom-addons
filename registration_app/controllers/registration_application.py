from odoo import http
# import datetime
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
import re
import base64


class RegistrationApplication(CustomerPortal):

    def validate_email(self, email):
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(regex, email)

    def validate_mobile_number(self, number):
        """Return True if the number is a valid Saudi mobile number."""
        regex = r'^(009665|9665|\+9665|05|5)(5|0|3|6|4|9|1|8|7)([0-9]{7})$'
        return re.match(regex, number)

    @http.route(['/upload-docs/<name>/<int:id>'], type='http', methods=["POST", "GET"], website=True, auth="public")
    def upload_docs(self, name=None, id=None, **kwargs):
        applicant = request.env["registration.application"].sudo().browse(id)
        qcontext = {'applicant': applicant}
        if not applicant.sudo().exists():
            return request.redirect("/")
        # Check if document is already uploaded
        if applicant.document:
            return request.render("registration_app.portal_upload_document_success")

        if request.httprequest.method == "POST":
            # Validate that the applicant name matches the name in the URL
            if applicant.applicatian_name != name:
                return request.redirect("/")

            # Validate that a file has been uploaded
            file = kwargs.get('pdf_file')
            if not file:
                qcontext['error'] = "Please upload a PDF file."
                return request.render("registration_app.upload_doc", qcontext=qcontext)

            # Validate the file is a PDF
            if file.content_type != 'application/pdf':
                qcontext['error'] = "Only PDF files are allowed."
                return request.render("registration_app.upload_doc", qcontext=qcontext)

            # Check file size (ensure it's within the 10 MB limit)
            max_size = 10 * 1024 * 1024  # 10 MB
            file.seek(0, 2)  # Move to end of file to check size
            file_size = file.tell()
            file.seek(0)  # Reset file pointer to beginning

            if file_size > max_size:
                qcontext['error'] = "The file size exceeds the maximum limit of 10 MB."
                return request.render("registration_app.upload_doc", qcontext=qcontext)

            # Upload the PDF file
            file_name = file.filename
            attachment_id = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'res_model': 'registration.application',
                'res_id': applicant.id,
            })

            # Link attachment to applicant
            applicant.sudo().write({'document': [(4, attachment_id.id)]})
            return request.render("registration_app.portal_upload_document_success")

        # Render the document upload form
        return request.render("registration_app.upload_doc", qcontext=qcontext)

    @http.route(['/registration_application/<course_name>/<int:course_id>/<name>',
    '/registration_application/<course_name>/<int:course_id>'],
                type='http', methods=["POST", "GET"], website=True, auth="public")
    def portal_registration_application(self, course_name=None, name=None, course_id=None, **kwargs):
        error_list = []
        context = {}
        nationalities = request.env['res.country'].sudo().search([])
        context['nationalities'] = nationalities
        # states = request.env['res.country.state'].sudo().search([('country_id.code', '=', 'SA')])
        # context['states'] = states
        # recruitment = False

        if request.httprequest.method == "GET":
            course = request.env["slide.channel"].sudo().browse(course_id)
            context['course'] = course
            if course.max_registration_application <= course.current_registration_application:
                return request.render('registration_app.portal_registration_application_full', qcontext=context)

            return request.render('registration_app.portal_registration_application_form_view', qcontext=context)

        elif request.httprequest.method == "POST":
            if not self.validate_email(kwargs.get('email')):
                error_list.append("Please Import Valid Email.")
            if not self.validate_mobile_number(kwargs.get('mobile')):
                error_list.append("Please Import Valid Saudian Mobile Number.")
            if len(kwargs.get('national_id')) != 10:
                error_list.append("Please Import Valid National ID.")
            if request.env["registration.application"].sudo().search_count([('applicatian_national_id', '=', kwargs.get('national_id'))]) > 0:
                error_list.append("This National ID Has Been Used Before.")
            if len(error_list) == 0:
                course = request.env["slide.channel"].sudo().browse(course_id)
                if course.max_registration_application <= course.current_registration_application:
                    return request.render('registration_app.portal_registration_application_full', qcontext=context)
                # print('------------------',kwargs.get('pdf_file').read())
                # file_name =kwargs.get('pdf_file').filename
                # file = kwargs.get('pdf_file')
                # attachment_id = request.env['ir.attachment'].create({
                #     'name': file_name,
                #     'type': 'binary',
                #     'datas': base64.b64encode(file.read()),
                #     'res_model': 'registration.application',
                # })
                vals: dict = {
                    'applicatian_name': kwargs.get('name'),
                    'course_id': course_id,
                    'applicatian_gender': kwargs.get('gender', False),
                    'applicatian_nationality': int(kwargs.get('country_id')) if kwargs.get('country_id', False) else False,
                    'applicatian_mobile': kwargs.get('mobile'),
                    'applicatian_national_id': kwargs.get('national_id'),
                    'applicatian_mail': kwargs.get('email'),
                    'is_applicatian_hadf_support': kwargs.get('has_support', False),
                    'is_applicatian_work': kwargs.get('has_work', False),
                    'is_applicatian_student': kwargs.get('is_student', False),
                    'applicatian_birth_date': kwargs.get('birth_date'),
                    'percentage_of_general_abilities': float(kwargs.get('abilities')) if kwargs.get('abilities', False) else False,
                    'high_school_percentage': float(kwargs.get('high_school')) if kwargs.get('high_school', False) else False,
                    # 'document': [(4, attachment_id.id)],
                }
                request.env["registration.application"].sudo().create(vals)
                return request.render("registration_app.portal_registration_application_success")
            # if recruitment and recruitment.exists():
            #     recruitment.sudo().write(vals)
            # else:
            #     request.env['recruitment.recruitment'].sudo().create(vals)
            context['error_message'] = error_list
            course = request.env["slide.channel"].sudo().browse(course_id)
            context['course'] = course
            context.update(kwargs)
            return request.render('registration_app.portal_registration_application_form_view', qcontext=context)
