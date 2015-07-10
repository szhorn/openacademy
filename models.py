from openerp import api,models,fields,exceptions
from datetime import timedelta

class Course(models.Model):
	_name = 'openacademy.course'

	name = fields.Char(string="Title",required=True)
	description = fields.Text()
	responsible_id = fields.Many2one('res.users',ondelete='set null',string="Responsible",index=True)
	session_ids = fields.One2many('openacademy.session','course_id',string="Session")
	example_field = fields.Char(string="Example Field")

	@api.one
	def copy(self,default=None):
		default = dict(default or {})

		copied_count = self.search_count([('name','=like',u"Copy of {}%".format(self.name))])
		if not copied_count:
			new_name = u"Copy of {}".format(self.name)
		else:
			new_name = u"Copy of {} ({})".format(self.name,copied_count)

		default['name'] = new_name
		return super(Course,self).copy(default)

	_sql_constraints = [
		(
			'name_description_check',
			'CHECK(name != description)',
			"The title of the course should not be the description"
			),
		(
			'name_unique',
			'UNIQUE(name)',
			"The course title must be unique"
			),
	]

class Session(models.Model):
	_name = "openacademy.session"

	name = fields.Char(required=True)
	start_date = fields.Date(default=fields.Date.today)
	duration = fields.Float(digits=(6,2),help="Duration in Days")
	seats = fields.Integer(string="Number of seats")
	instructor_id = fields.Many2one('res.partner',string="Instructor",domain=['|',('instructor','=',True),('category_id.name','ilike','Teacher')])
	course_id = fields.Many2one('openacademy.course',ondelete='cascade',string="Course",required=True)
	attendee_ids = fields.Many2many('res.partner',string="Attendees")
	taken_seats = fields.Float(string="Taken Seats",compute="_taken_seats")
	active = fields.Boolean(default=True)
	end_date = fields.Date(string="End Date",store=True,compute='_get_end_date',inverse='_set_end_date')
	hours = fields.Float(string="Duration in hours",compute='_get_hours',inverse='_set_hours')
	attendees_count = fields.Integer(string="Attendees count",compute='_get_attendees_count',store=True)
	color = fields.Integer()
	state = fields.Selection([
		('draft',"Draft"),
		('confirmed',"Confirmed"),
		('done',"Done"),
		],default="draft")
	partner_id = fields.Many2one('res.partner',string="Partner")
	address = fields.Char(string="Address",related='partner_id.street')

	@api.one
	def action_draft(self):
		self.state = 'draft'

	@api.one
	def action_confirm(self):
		self.state = 'confirmed'

	@api.one
	def action_done(self):
		self.state = 'done'

	@api.one
	@api.depends('seats','attendee_ids')
	def _taken_seats(self):
		if not self.seats:
			self.taken_seats = 0.0
		else:
			self.taken_seats = 100.0 * len(self.attendee_ids) / self.seats

	@api.onchange('seats','attendee_ids')
	def _verify_valid_seats(self):
		if self.seats < 0:
			return {
				'warning' : {
					'title' : "Incorrect 'seats' value",
					'message' : "The number of available seats may not be negative",
				},
			}
		if self.seats < len(self.attendee_ids):
			return {
				'warning' : {
					'title' : "Too many Attendees ",
					'message' : "Increase seats or remove excess attendees",
				},
			}

	@api.one
	@api.constrains('instructor_id','attendee_ids')
	def _check_instructor_not_in_attendees(self):
		if self.instructor_id and self.instructor_id in self.attendee_ids:
			raise exceptions.ValidationError("A session's instructor can't be an attendee")

	@api.one
	@api.depends('start_date','duration')
	def _get_end_date(self):
		if not (self.start_date and self.end_date):
			self.end_date = self.start_date
			return

		start = fields.Datetime.from_string(self.start_date)
		duration = timedelta(day=self.duration,seconds=-1)
		self.end_date = start + duration

	@api.one
	def _set_end_date(self):
		if not(self.start_date and self.end_date):
			return

		start_date = fields.Datetime.from_string(self.start_date)
		end_date = fields.Datetime.from_string(self.end_date)
		self.duration = (end_date - start_date).days + 1

	@api.one 
	def _get_hours(self):
		self.hours = self.duration * 24

	@api.one
	def _set_hours(self):
		self.duration = self.hours / 24

	@api.one
	@api.depends('attendee_ids')
	def _get_attendees_count(self):
		self.attendees_count = len(self.attendee_ids)