{
    'name' : "Open Academy",
    'summary' : """Manage trainings""",
    'description' : """
        Open Academy module for managing traingings
            - training courses
            - training sessions
            - attendees registration
    """,
    'author' : "Frank",
    'website' : "www.szhorn.com",
    'category' : 'Test',
    'version' : '1.0',
    'depends' : ['base'],
    'data' : [
        'templates.xml',
        'views/openacademy.xml',
        'views/res_partner_view.xml',
        'views/session_workflow.xml',
        'reports.xml',
    ],
    'demo' : [
        
    ],
}