# from pdb import set_trace
from openerp.http import Response
from odoo.http import request, route
import werkzeug
import requests
import pytz
from odoo.addons.mobikul.tool.service import WebServices
from odoo.addons.http_routing.models.ir_http import slug
from odoo import http, _
from odoo.http import request, route
from odoo.http import request, Controller, route

from odoo.fields import Datetime, Date, Selection
from odoo.exceptions import UserError
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import date, datetime, timedelta
import urllib
import urllib.request
import urllib.parse
from uuid import uuid4


try:
    from urllib.parse import urlencode
    from urllib.request import build_opener, Request, HTTPHandler
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib import urlencode
    from urllib2 import build_opener, Request, HTTPHandler, HTTPError, URLError

import json
import re
import math
import random
import logging
_logger = logging.getLogger(__name__)


class MobikulApi(WebServices):


    @route('/wallet/loginphone', csrf=False, type='http', auth="public", methods=['POST'])
    def loginphone(self,  **kwargs):
            msg =''
            success = False
            values =[]
            username = kwargs['username']
            password = kwargs['password']
            user_id = request.env['res.partner'].sudo().search([('identification', '=', username),('password', '=', password),('responsable_rank', '=', True)], limit=1)

            if user_id :
                user_id.sudo().rand_token = uuid4()
                values.append({'user': user_id.identification,
                          'passwd': user_id.password,
                          'name': user_id.full_name,
                          'mobilenumber': user_id.phone,
                           'token':user_id.rand_token })
                success = True
                status = 200
                
               # return Response( json.dumps(values) , status=status)   
            else:
                msg = "Username or password error"
                status = 401
              #  return Response( msg , status=status)

            print (">>>>>>>>>>>>>>>>>>>>>>>>>>>> user_id.rand_token = ",user_id.rand_token)
            loginphone = { 'success' : success,
                           'data': values,
                            'message': msg}
            return self._myresponse('loginphone', loginphone,status)



    def _myresponse(self, apiName, response,  status,ctype='json'):
        if response.get("context"):
            response.pop("context")
        if 'local' in response:
            response.pop("local")
        if ctype == 'json':
            mime = 'application/json; charset=utf-8'
            body = json.dumps(response)
        else:
            mime = 'text/xml'
            body = self._wrap2xml(apiName, response)
        headers = [
            ('Content-Type', mime),
            ('Content-Length', len(body))
        ]
        return werkzeug.wrappers.Response(body, headers=headers, status=status)




    @route('/wallet/getStudensInWallet', csrf=False, type='http', auth="public", methods=['GET'])
    def getStudensInWallet(self, **kwargs):

        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            msg =''
            success = False
            values =[]
            username = kwargs['username']
            rand_token  = request.httprequest.headers.get('Rand-Token')
            user_id = request.env['res.partner'].sudo().search([('identification', '=', username)], limit=1)
            if not user_id :
                msg = 'This user not found'
                status = 404
            else:
                print ("")
                if user_id.rand_token != rand_token :
                    status = 401
                    msg = 'invalid token'
                else:
                    wallet_id = request.env['e.wallet'].sudo().search([('responsable', '=', user_id.id)], limit=1)
                    if not wallet_id :
                        msg = 'This user dose not have wallet'
                        status = 404
                    if wallet_id:
                        for line in wallet_id.line_ids:
                            values.append({'student_id': line.student.id,
	    			       'student_name': line.student.name,
                                        'limit': line.limit,
                                        'amount': line.amount,
  				})
                    
                        
                        success = True
                        status = 200
                        if not values:
                            success = False
                            status = 404
                            msg='No Student in your wallet'

            loginphone = { 'success' : success,
                           'data': values,
                            'message': msg}
            return self._myresponse('loginphone', loginphone,status)




    @route('/wallet/addStudenToMyWallet', csrf=False, type='http', auth="public", methods=['POST'])
    def addStudenToMyWallet(self, **kwargs):
        print('type_id----------------------------------',kwargs)
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            msg =''
            success = False
            values =[]
            username = kwargs['username']
            student_id = kwargs['student']
            limit = kwargs['limit']
            rand_token  = request.httprequest.headers.get('Rand-Token')
            user_id = request.env['res.partner'].sudo().search([('identification', '=', username)], limit=1)
            student = request.env['res.partner'].sudo().search([('identification', '=', student_id),('student_rank', '=', True)], limit=1)
            if not user_id :
                msg = 'This user not found'
                status = 404
            else:
                
                if user_id.rand_token != rand_token :
                    status = 401
                    msg = 'invalid token'
                else:

                    wallet_id = request.env['e.wallet'].sudo().search([('responsable', '=', user_id.id)], limit=1)
                    if not wallet_id :
                        msg = 'This user dose not have wallet'
                        status = 404
                    if wallet_id:


                        if not student :
                            success = False
                            status = 401
                            msg='this student dose not exist'
                        if student :
                            flag = False 
                            for line in wallet_id.line_ids:
                                if student == line.student :
                                    flag = True 
                            if flag:
                                msg = 'This student is already added to your wallet'
                                status = 404
                            else:

                                student.in_wallet =  True
                                student.needy =  False
                                student.responsable = user_id.id
                               
                                request.env['wallet.line'].sudo().create({
				    'student': student.id,
				    'limit': limit,
				    'wallet':wallet_id.id}) 
                                success = True
                                status = 200
                                values.append({'student': student.name,
	    			          'School': student.school_id.name,
                                       
  				})

            loginphone = { 'success' : success,
                           'data': values,
                            'message': msg}
            return self._myresponse('loginphone', loginphone,status)





    @route('/wallet/walletFeeding', csrf=False, type='http', auth="public", methods=['POST'])
    def walletFeeding(self, **kwargs):
        rand_token = uuid4()
        
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            msg =''
            success = False
            values =[]
            username = kwargs['username']
            amount = kwargs['amount']
            rand_token  = request.httprequest.headers.get('Rand-Token')

            user_id = request.env['res.partner'].sudo().search([('identification', '=', username)], limit=1)
            if not user_id :
                msg = 'This user not found'
                status = 404
            else:
                if user_id.rand_token != rand_token :
                    status = 401
                    msg = 'invalid token'

                else:
                    wallet_id = request.env['e.wallet'].sudo().search([('responsable', '=', user_id.id)], limit=1)
                    if not wallet_id :
                        msg = 'This user dose not have wallet'
                        status = 404
                    if wallet_id:
                        new_transaction = request.env['wallet.transactions'].sudo().create({
	                        'wallet': wallet_id.id,
	                        'amount': amount,
	                        'transaction_type':'credit',
	                     #  'currency_id':self.wallet.currency_id.id,
                            })
                        new_transaction.state='done'
                        success = True
                        status = 200
                        msg='OK'

            loginphone = { 'success' : success,
                           'data': values,
                            'message': msg}
            return self._myresponse('loginphone', loginphone,status)




    @route('/wallet/removeStudenFromMyWallet', csrf=False, type='http', auth="public", methods=['POST','DELETE'])
    def removeStudenFromMyWallet(self, **kwargs):
        rand_token = uuid4()
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            msg =''
            success = False
            values =[]
            username = kwargs['username']
            student_id = kwargs['student']
            student = request.env['res.partner'].sudo().search([('identification', '=', student_id),('student_rank', '=', True)], limit=1)
            user_id = request.env['res.partner'].sudo().search([('identification', '=', username)], limit=1)
            rand_token  = request.httprequest.headers.get('Rand-Token')
            if not user_id :
                msg = 'This user not found'
                status = 404
            if user_id:
                wallet_id = request.env['e.wallet'].sudo().search([('responsable', '=', user_id.id)], limit=1)
                if user_id.rand_token != rand_token :
                    status = 401
                    msg = 'invalid token'

                else:
                    if not wallet_id :
                        msg = 'This user dose not have wallet'
                        status = 404
                    if wallet_id:
                        line_id = request.env['wallet.line'].sudo().search([('wallet', '=', wallet_id.id),('student', '=',student.id)], limit=1)
                        if not line_id :
                            msg = 'This student not in your wallet'
                            status = 404
                        else:
                            line_id.sudo().unlink()
                            student = student
                            student.in_wallet =  False
                            student.needy =  True
                            success = True
                            status = 200
                            msg='OK'
            loginphone = { 'success' : success,
                           'data': values,
                           'message': msg }
            return self._myresponse('loginphone', loginphone,status)





    @route('/wallet/registration', csrf=False, type='http', auth="public", methods=['POST'])
    def registration(self,  **kwargs):
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):

            msg =''
            success = False
            values =[]
            id_number = kwargs['id_number']
            


            kwargs = {
            'auth':'Basic U2FzQWRtV2F5czpQc1dzQWQlNTQ2NSYj',
            'adName': account.adName,
            'adPass': account.adPass,
            'uName': self.uName,
            'uPass': self.uPass,
            'company': self.company,
            'ResponsibleName': self.ResponsibleName,
            'Company_regn': self.Company_regn,
            'email': self.email,
            'mobile': self.mobile,
            'country_code': self.country_code,
            'City': self.City,
            'phone': self.phone,
            'credits': account.credits,
            'address': self.address,
            'sender': self.sender,
             }


            

            user_id = request.env['res.partner'].sudo().search([('identification', '=', username),('password', '=', password),('responsable_rank', '=', True)], limit=1)

            if user_id :
                user_id.rand_token = uuid4()
                values.append({'user': user_id.identification,
                               'passwd': user_id.password,
                               'name': user_id.full_name,
                               'mobilenumber': user_id.phone,
                             'token':user_id.rand_token })
                success = True
                status = 200
                
               # return Response( json.dumps(values) , status=status)   
            else:
                msg = "Username or password error"
                status = 401
              #  return Response( msg , status=status)


            loginphone = { 'success' : success,
                           'data': values,
                            'message': msg}
            return self._myresponse('loginphone', loginphone,status)



 

    @route('/wallet/getTransactions', csrf=False, type='http', auth="public", methods=['GET'])
    def getTransactions(self, **kwargs):

        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
 
        if response.get('success'):
            msg =''
            success = False
            values =[]
            username = kwargs['username']
            rand_token  = request.httprequest.headers.get('Rand-Token')
            user_id = request.env['res.partner'].sudo().search([('identification', '=', username)], limit=1)
            if not user_id :
                msg = 'This user not found'
                status = 404
            else:
                if user_id.rand_token != rand_token :
                    status = 401
                    msg = 'invalid token'
                else:
                    wallet_id = request.env['e.wallet'].sudo().search([('responsable', '=', user_id.id)], limit=1)
                    if not wallet_id :
                        msg = 'This user dose not have wallet'
                        status = 404
                    if wallet_id:
                        domain = [('wallet', '=', wallet_id.id)]
                        if 'date_from' in kwargs:
                            domain.append(('transaction_date','>=',kwargs['date_from']))
                        if 'date_to' in kwargs:
                            domain.append(('transaction_date','<=',kwargs['date_to']))
                        if 'student' in kwargs:
                            student = request.env['res.partner'].sudo().search([('identification', '=', kwargs['student'])], limit=1)
                      
                            domain.append(('partner_id','=',student.id))

                        transactions = request.env['wallet.transactions'].sudo().search(domain)
                        for line in transactions:
                            date = str(line.transaction_date.date())
                            
                            values.append({'student': line.partner_id.id,
	    			           'amount': line.amount,
                                           'type': line.transaction_type,
                                           'date': date,
  				})
                    
                        
                        success = True
                        status = 200
                        if not values:
                            success = False
                            status = 404
                            msg='No transactions in your wallet'
            print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>. values =",values)
            loginphone = { 'success' : success,
                           'data': values,
                            'message': msg}
            return self._myresponse('loginphone', loginphone,status)





    @route('/wallet/changeStudentLimit', csrf=False, type='http', auth="public", methods=['POST'])
    def changeStudentLimit(self, **kwargs):
        print('type_id----------------------------------',kwargs)
        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            msg =''
            success = False
            values =[]
            username = kwargs['username']
            student_id = kwargs['student']
            limit = kwargs['limit']
            rand_token  = request.httprequest.headers.get('Rand-Token')
            user_id = request.env['res.partner'].sudo().search([('identification', '=', username)], limit=1)
            student = request.env['res.partner'].sudo().search([('identification', '=', student_id),('student_rank', '=', True)], limit=1)
            status = 200
            if not user_id :
                msg = 'This user not found'
                status = 404
            else:
                
                if user_id.rand_token != rand_token :
                    status = 401
                    msg = 'invalid token'
                else:

                    wallet_id = request.env['e.wallet'].sudo().search([('responsable', '=', user_id.id)], limit=1)
                    if not wallet_id :
                        msg = 'This user dose not have wallet'
                        status = 404
                    if wallet_id:


                        if not student :
                            success = False
                            status = 401
                            msg='this student dose not exist'
                        if student :
                            student_line = request.env['wallet.line'].sudo().search([('wallet', '=', wallet_id.id),('student', '=', student.id)], limit=1)
                            if not student_line:
                                msg = 'This student not in your wallet'
                                status = 404
                            else:
                                student_line.limit = limit
                                values.append({'student': student_line.student.name,
	    			          'School': student_line.student.school_id.name,
                                           'limit':student_line.limit
                                   
                                       
  				})
                                status = 200
                                success = True
                                msg = 'Done'

            loginphone = { 'success' : success,
                           'data': values,
                            'message': msg}
            return self._myresponse('loginphone', loginphone,status)





    @route('/wallet/getWalletAmount', csrf=False, type='http', auth="public", methods=['GET'])
    def getWalletAmount(self, **kwargs):

        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
        if response.get('success'):
            msg =''
            success = False
            values =[]
            username = kwargs['username']
            rand_token  = request.httprequest.headers.get('Rand-Token')
            user_id = request.env['res.partner'].sudo().search([('identification', '=', username)], limit=1)
            if not user_id :
                msg = 'This user not found'
                status = 404
            else:
                print ("")
                if user_id.rand_token != rand_token :
                    status = 401
                    msg = 'invalid token'
                else:
                    wallet_id = request.env['e.wallet'].sudo().search([('responsable', '=', user_id.id)], limit=1)
                    if not wallet_id :
                        msg = 'This user dose not have wallet'
                        status = 404
                    if wallet_id:
                            values.append({'user': wallet_id.responsable.name,
	    			       'amount': wallet_id.transactions_count,
                                       
  				})
                    
                        
                            success = True
                            status = 200
                        

            loginphone = { 'success' : success,
                           'data': values,
                            'message': msg}
            return self._myresponse('loginphone', loginphone,status)




    @route('/wallet/getOrders', csrf=False, type='http', auth="public", methods=['GET'])
    def getOrders(self, **kwargs):

        if request.httprequest.headers.get("Login"):
            response = self._authenticate(True, **kwargs)
        else:
            response = self._authenticate(False, **kwargs)
 
        if response.get('success'):
            msg =''
            success = False
            values =[]
            username = kwargs['username']
            rand_token  = request.httprequest.headers.get('Rand-Token')
            user_id = request.env['res.partner'].sudo().search([('identification', '=', username)], limit=1)
            if not user_id :
                msg = 'This user not found'
                status = 404
            else:
                if user_id.rand_token != rand_token :
                    status = 401
                    msg = 'invalid token'
                else:
                    wallet_id = request.env['e.wallet'].sudo().search([('responsable', '=', user_id.id)], limit=1)
                    if not wallet_id :
                        msg = 'This user dose not have wallet'
                        status = 404
                    if wallet_id:
                        domain = [('wallet', '=', wallet_id.id)]
                        if 'date_from' in kwargs:
                            domain.append(('transaction_date','>=',kwargs['date_from']))
                        if 'date_to' in kwargs:
                            domain.append(('transaction_date','<=',kwargs['date_to']))
                        if 'student' in kwargs:
                            student = request.env['res.partner'].sudo().search([('identification', '=', kwargs['student'])], limit=1)
                      
                            domain.append(('partner_id','=',student.id))

                        transactions = request.env['wallet.transactions'].sudo().search(domain)
                        for line in transactions:
                            date = str(line.transaction_date.date())
                            order_ids = request.env['pos.order'].sudo().search([('pos_reference', '=', line.pos_order)])
                            for order in order_ids:
                                for o_line in order.lines:
                                    values.append({'student': line.partner_id.id,
                                                   'type': o_line.product_id.name,
                                                   'qty': o_line.qty,
                                                    
	    			                   'amount': o_line.price_subtotal_incl,
                                                   'date': date,
  				})
                    
                        
                        success = True
                        status = 200
                        if not values:
                            success = False
                            status = 404
                            msg='No transactions in your wallet'
            print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>. values =",values)
            loginphone = { 'success' : success,
                           'data': values,
                            'message': msg}
            return self._myresponse('loginphone', loginphone,status)



class WebServices(Controller):
    def _available_api(self):
        API = {

                '/wallet/loginphone':
                {'description': 'post loginphone',
                 'url': '/wallet/loginphone',},


  
                'getStudensInWallet':
                {'description': 'get getStudensInWallet',
                 'url': '/wallet/getStudensInWallet',},
               




                '/wallet/addStudenToMyWallet':
                {'description': 'post addStudenToMyWallet',
                 'url': '/wallet/addStudenToMyWallet',},


                '/wallet/removeStudenFromMyWallet':
                {'description': 'post delete removeStudenFromMyWallet',
                 'url': '/wallet/removeStudenFromMyWallet',},


                '/wallet/walletFeeding':
                {'description': 'post walletFeeding',
                 'url': '/wallet/walletFeeding',},
               

                'getTransactions':
                {'description': 'get getTransactions',
                 'url': '/wallet/getTransactions',},

              
                'changeStudentLimit':
                {'description': 'post changeStudentLimit',
                 'url': '/wallet/changeStudentLimit',},

                'getWalletAmount':
                {'description': 'get getWalletAmount',
                 'url': '/wallet/getWalletAmount',},


                'getOrders':
                {'description': 'get getOrders',
                 'url': '/wallet/getOrders',},

               
        }
        return API
