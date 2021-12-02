import logging
import werkzeug
import json
from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo.http import request
import urllib
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home

_logger = logging.getLogger(__name__)
import requests

import passlib.context
import math, random 


def generateOTP() : 
    digits = "0123456789"
    OTP = "" 
    for i in range(4) : 
        OTP += digits[int(math.floor(random.random() * 10))] 
    return '1234'

class OAuthLoginOtp(Home):
	

    def get_auth_signup_config(self):
    	response = super(OAuthLoginOtp, self).get_auth_signup_config()
    	company_id = request.env['res.company'].sudo().search([('id','=',1)])
    	response.update({
    
    			'signup_otp': company_id.use_otp_login,
    		})
    	return response
    
    @http.route('/phoneexist', type='http', auth="public", website=True, methods=['GET'], csrf=False)
    def validate_referral_code(self, **kwargs):
    	"""Controller for validating referral codes"""
    	result_dict = {}
    	params_keys = list(kwargs.keys())
    	phone = kwargs['sendto']
    	name = kwargs['name']
    	if phone and name:
    	    partner_ids = request.env['res.users'].sudo().search(['|',('phone','=',phone),('login','=',name)])
    	    if partner_ids:
    	        return "False"
    	    else:
    	    	return "True"
    	return json.dumps(result_dict)
	
    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password','otp','phone') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        user_id = request.env['res.users'].sudo().search([('phone','=',values.get('phone'))])
        if user_id:
        	raise UserError(_("Phone number is already registered."))
        if values.get('phone'):
            if len(values.get('phone')) != 10 or not values.get('phone').isdigit():
                raise UserError(_("Not a valid Phone Number."))
        
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    
		
    @http.route('/web/request_otp', type='http', auth='public', website=True, sitemap=False)
    def web_auth_request_otp(self, *args, **kw):

        qcontext = request.params.copy()
        try:
            if qcontext.get('mobile'):
                user_id = request.env['res.users'].sudo().search([('phone', '=', qcontext.get('mobile'))], limit=1)
                if user_id:
                    qcontext.update({'user': user_id.id})
                    otp = generateOTP()
                    print(otp)
                    company_id = request.env['res.company'].sudo().search([('id','=',1)])
                    if company_id and company_id.otp_message:
                        if '%s' not in company_id.otp_message:
                            text = str(company_id.otp_message)+ str(otp)
                        else:
                            text = str(company_id.otp_message).replace('%s',otp)
                    else:
                        text = """Dear Customer,
%s is your one time password (OTP). Please enter the OTP to proceed.
Thank you,
Team Seeroo"""%otp
                            
                    data_url = ''
                    print(otp)
                    print('heelo')
                        
                    try:
                        # if company_id and company_id.use_otp_login:
                        #     data_url = company_id and company_id.otp_message_url or ''
                        #     phone_key = company_id and str(company_id.phone_key) or ''
                        #     message_key = company_id and str(company_id.message_key) or ''
                        #
                        #     data_url = str(data_url).replace(phone_key,str("91"+qcontext.get('mobile')))
                        #     data_url = str(data_url).replace(message_key,str(text))
                        #
                        # result = requests.post(data_url, timeout=20)
                        qcontext.update({'otp_original': otp})
                        response = request.render('sr_otp_login.verify_otp', qcontext)

                        return response
                    except:
                        response = request.render('sr_otp_login.request_otp', qcontext)
                        return response
                    
                else:
                    try:

                        otp = generateOTP()
                        qcontext.update({'otp_original': otp})
                        do_signup={'phone': qcontext.get('mobile'),
                                    'login':qcontext.get('mobile'),
                                    'name':qcontext.get('mobile'),
                                   'otp':otp,
                                   'sel_groups_1_8_9':'8',
                                   }
                        user_id=request.env['res.users'].sudo().create(do_signup)
                        qcontext.update({'user': user_id.id})



                        print('hello signup')
                        # do_signup(do_signup)
                        response = request.render('sr_otp_login.verify_otp', qcontext)
                        print('new user1')
                        return response

                       # raise UserError(_('This Mobile number is not registered..'))
                    #except UserError as e:
                    except:
                        print('new user2')
                        response = request.render('sr_otp_login.request_otp', qcontext)
                        return response
                        # qcontext['error'] = e.name or e.value
                        # response = request.render('sr_otp_login.request_otp', qcontext)
                        # return response

            if qcontext.get('otp_one') and qcontext.get('otp_two') and qcontext.get('otp_three') and qcontext.get('otp_four'):
                otp_customer =  str(qcontext.get('otp_one')+qcontext.get('otp_two')+qcontext.get('otp_three')+qcontext.get('otp_four'))
                if otp_customer != qcontext.get('otp_original'):
                    try:
                        raise UserError(_('Verification Failed'))
                    except UserError as e:
                        qcontext['error'] = e.name or e.value
                        response = request.render('sr_otp_login.verify_otp', qcontext)
                        return response
                else:
                    user_id = request.env['res.users'].sudo().search([('id', '=', qcontext.get('user'))], limit=1)
                    request.env.cr.execute(
                        "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
                        [qcontext.get('user')]
                    )
                    hashed = request.env.cr.fetchone()[0]
                    qcontext.update({'login': user_id.sudo().login,
                                     'name': user_id.sudo().partner_id.name,
                                     'password': hashed + 'mobile_otp_login'})
                    print(hashed + 'mobile_otp_login')
                    request.params.update(qcontext)
                    return self.web_login(*args, **kw)

        except UserError as e:
            qcontext['error'] = e.name or e.value
            
            
        response = request.render('sr_otp_login.request_otp', {})
        return response
