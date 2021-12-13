# Constants
SCHEDULE_TYPES = {
    '': 'Not Listed',

    'BUS': 'Bus Transportation',
    'COP': 'Cooperative Education',
    'CLP': 'Clinical Practice',
    'CNF': 'Conference',
    'DIS': 'Discussion',
    'FL': 'Flight',
    'LAB': 'Labratory',
    'LEC': 'Lecture',
    'LCD': 'Lecture-Discussion',
    'IND': 'Independent Study',
    'INT': 'Intership',
    'LBD': 'Labratory-Discussion',
    'ONL': 'Online',
    'OD': 'Online Discussion',
    'OLC': 'Online Lecture',
    'OLB': 'Online Lab',
    'OLD': 'Online Lecture-Discussion',
    'PKG': 'Package',
    'PR': 'Practice',
    'Q': 'Quiz',
    'RES': 'Research',
    'SEM': 'Seminar',
    'ST': 'Studio',
    'STA': 'Study Abroad',
    'TRV': 'Travel',
}

# Database Settings
HOST = 'localhost'
PORT = '5432'
USER = ''
PASSWORD = 'password'
DATABASE = 'classy_course'

# Tables
TABLES = {}
TABLES['grades'] = (
    "CREATE TABLE IF NOT EXISTS grades ("
    " id serial PRIMARY KEY,"

    " year INT NOT NULL,"
    " term VARCHAR(16) NOT NULL,"
    " subject VARCHAR(16) NOT NULL,"
    " number INT NOT NULL,"
    " name VARCHAR(255) NOT NULL,"
    " instructor VARCHAR(255) NOT NULL,"

    " sched_type VARCHAR(16),"

    " a_plus INT DEFAULT 0,"
    " a INT DEFAULT 0,"
    " a_minus INT DEFAULT 0,"
    " b_plus INT DEFAULT 0,"
    " b INT DEFAULT 0,"
    " b_minus INT DEFAULT 0,"
    " c_plus INT DEFAULT 0,"
    " c INT DEFAULT 0,"
    " c_minus INT DEFAULT 0,"
    " d_plus INT DEFAULT 0,"
    " d INT DEFAULT 0,"
    " d_minus INT DEFAULT 0,"
    " f INT DEFAULT 0,"
    " w INT DEFAULT 0"
    ")"
)