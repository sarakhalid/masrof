# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from openerp.osv import  osv, expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.tools import remove_accents
import logging
import re

class schoolschool(models.Model):
    _name = "school.school"


class ResCompany(models.Model):
    _inherit = "res.company"
 



    @api.depends('student_ids')
    def _compute_student_ids(self):
        for order in self:
            order.student_count = len(order.student_ids)



    def action_view_student(self):
        action = self.env.ref('e_wallet.res_partner_action_student').read()[0]
        students = self.mapped('student_ids')
        if len(students) > 1:
            action['domain'] = [('id', 'in', students.ids)]
        elif students:
            form_view = [(self.env.ref('base.view_partner_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = students.id
        # Prepare the context.
        student_id = students
        if student_id:
            student_id = student_id[0]
        else:
            if students:
                student_id = students[0]
        return action





    ministerial_number = fields.Char(string="Ministerial number"  ) 
    phone = fields.Char(string="Phone" ) 
    school_type = fields.Many2one('school.type', string='Educational level')
    education_type = fields.Selection([('governmental', 'Governmental'), ('local', 'Local '),  ], string="Education Type")
    period = fields.Selection([('morning', 'Morning'), ('evening', 'Evening '), ('night', 'Night ') ], string="Period")
    building_type = fields.Selection([('governmental', 'Governmental'), ('tenant', 'Tenant'),('special', 'Special') ], string="Building Type")

    manager_id = fields.Many2one('res.users', string='Manager',domain=[('partner_type','=','s_manager')])
    fund_officer = fields.Many2one('res.users', string='Fund officer',domain=[('partner_type','=','fund_officer')])
    student_advisor = fields.Many2one('res.users', string='Student Advisor ' ,domain=[('partner_type','=','s_advisor')])


    education_id = fields.Many2one('education.administration', string='Education Administration')

    student_ids = fields.One2many('res.partner', 'school_id', string='Students')
    student_count = fields.Integer(string='students count', compute='_compute_student_ids')


class SchoolType(models.Model):
    _name = 'school.type'
 
    name = fields.Char(string="Name"  , required=True) 
    limit = fields.Float(string='Limit')



class ClassRoom(models.Model):
    _name = 'class.room'
 
    name = fields.Char(string="Name"  , required=True) 

class StudentsNeed(models.Model):
    _name = 'students.need'
 
    date = fields.Date(string="Date") 
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], string="State",default='draft')
    students_ids = fields.One2many('need.line','need_id', string='Students')

    def confirm_action(self):
        for line in self.students_ids:

            line.name.needy = True
        self.state ='confirmed'


class NeedLine(models.Model):
    _name = 'need.line'
 
    name = fields.Many2one('res.partner', string='Name',domain=[('student_rank','=',True),('in_wallet','=',True)])
    need_id = fields.Many2one('students.need', string='Need')



class SchoolCalendar(models.Model):
    _name = 'school.calendar'
 
    date_start = fields.Date(string="Date"  , required=True) 
    date_stop = fields.Date(string="Date Stop"  , required=True) 
    semester_id = fields.Many2one('school.semester', string='Semester', required=True)
    day_type = fields.Selection([('work_day', 'Work day'), ('holiday', 'Holiday')], string="Type",default='work_day', required=True)
    school_id = fields.Many2one('res.company', string='School', required=True, default=lambda self: self.env.company)


    @api.onchange('date_start')
    def _onchange_date_start(self):
        self.date_stop = self.date_start



class SchoolSemester(models.Model):
    _name = 'school.semester'
 
    name = fields.Char(string="Name"  , required=True) 
