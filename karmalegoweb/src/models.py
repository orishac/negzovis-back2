import datetime

from karmalegoweb.src.db import get_db

db = get_db()


class data_file(db.Model):
    uuid = db.Column(db.String(80), primary_key=True)
    owner = db.Column(db.String(80), db.ForeignKey("users.Email"), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    uploaded_successfully = db.Column(db.Boolean(), default=False)


class Users(db.Model):
    """
    This is the Users Table.
    It is in charge of maintaining data on Users, with the User's Email address as its Primary Key.
    """

    Email = db.Column(db.String(80), primary_key=True)
    institute = db.Column(db.String(50), nullable=False)
    degree = db.Column(db.String(10), nullable=False)
    Password = db.Column(db.String(200), nullable=False)
    FName = db.Column(db.String(50), nullable=False)
    LName = db.Column(db.String(50), nullable=False)
    my_datasets = db.relationship("info_about_datasets", backref="owner", lazy="subquery")
    Permissions = db.relationship("Permissions", backref="owner", lazy="subquery")
    ask_permissions = db.relationship("ask_permissions", backref="owner", lazy="subquery")


class info_about_datasets(db.Model):
    """
    This table is in charge of holding metadata on Datasets in the system, with the Dataset's name as its Primary Key.
    Information such as the Dataset's description or categorization goes here,
    while the content itself (the actual data etc.) is stored systematically in the "Datasets" folder
    """

    Name = db.Column(db.String(150), primary_key=True)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    Description = db.Column(db.String(255))
    public_private = db.Column(db.String(8), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Float, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    downloads = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(100))
    uploaded = db.Column(db.Boolean(), default=False)
    # TODO: Change the name to "owner"
    Email = db.Column(db.String(80), db.ForeignKey("users.Email"), nullable=False)
    Permissions = db.relationship("Permissions", backref="dataset", lazy="subquery")
    visual_reference = db.Column(db.String(350), nullable=False)
    ask_permissions = db.relationship("ask_permissions", backref="dataset", lazy="subquery")
    discretization = db.relationship("discretization", backref="dataset", lazy="subquery")
    class_0_name = db.Column(db.String(100), default="Cohort")
    class_1_name = db.Column(db.String(100), default="Control")


class Permissions(db.Model):
    """
    This table holds all the permissions in the system.
    It represents a Many-To-Many relationship between the Users table and the info_about_datasets table,
    with [Email,Dataset_Name] as its Composite Key.
    The existence of a tuple t such that t.Email = e and t.name_of_dataset = d signifies that e has permission to use d.
    """

    Email = db.Column(db.String(30), db.ForeignKey("users.Email"), primary_key=True)
    name_of_dataset = db.Column(
        db.String(50), db.ForeignKey("info_about_datasets.Name"), primary_key=True
    )


class ask_permissions(db.Model):
    """
    This table holds all the permission requests in the system.
    It represents a Many-To-Many relationship between the Users table and the info_about_datasets table,
        with [Email,Dataset_Name] as its Composite Key.
    The existence of a tuple t such that t.Email = e and t.name_of_dataset = d
        signifies that e has asked for permission to use d.
    """

    Email = db.Column(db.String(30), db.ForeignKey("users.Email"), primary_key=True)
    name_of_dataset = db.Column(
        db.String(50), db.ForeignKey("info_about_datasets.Name"), primary_key=True
    )


class discretization_status(db.Model):
    discretization_id = db.Column(
        db.String(150), db.ForeignKey("discretization.id"), primary_key=True
    )
    finished = db.Column(db.Boolean, nullable=False, default=False)
    success = db.Column(db.Boolean, nullable=True)
    msg = db.Column(db.String(150), nullable=True)


class discretization(db.Model):
    """
    This table holds all the info about the discretizations.
    Its primary key is a unique Discretization ID.
    In case we are dealing with a Gradient/Knowledge-based discretization,
    the files themselves are checked for uniqueness.
    The files of the discretization itself (states file, KL input file etc.) are stored systematically,
    in "Datasets/<Dataset Name>/<Disc Id>/".
    """

    id = db.Column(db.String(150), primary_key=True)
    PAA = db.Column(db.Integer)
    AbMethod = db.Column(db.String(25), nullable=False)
    NumStates = db.Column(db.Integer)
    InterpolationGap = db.Column(db.Integer)
    KnowledgeBasedFile_name = db.Column(db.String(120))
    GradientFile_name = db.Column(db.String(120))
    GradientWindowSize = db.Column(db.Integer)
    karma_lego = db.relationship("karma_lego", backref="discretization", lazy="subquery")
    dataset_Name = db.Column(
        db.String(150), db.ForeignKey("info_about_datasets.Name"), nullable=False
    )


class karmalego_status(db.Model):
    karmalego_id = db.Column(db.String(150), db.ForeignKey("karma_lego.id"), primary_key=True)
    finished = db.Column(db.Boolean, nullable=False, default=False)
    success = db.Column(db.Boolean, nullable=True)
    msg = db.Column(db.String(150), nullable=True)


class run(db.Model):
    id = db.Column(db.String(150), primary_key=True)
    finished = db.Column(db.Boolean, nullable=False, default=False)
    success = db.Column(db.Boolean, nullable=True)
    msg = db.Column(db.String(150), nullable=True)


class karma_lego(db.Model):
    """
    This table holds all the info about the KarmaLego runs.
    Its primary key is a unique KarmaLego ID
    The output file(s) is/are stored separately in "Datasets/<Dataset Name>/<Disc Id>/<KL Id>/".
    """

    id = db.Column(db.String(150), primary_key=True)
    epsilon = db.Column(db.Float)
    min_ver_support = db.Column(db.Float, nullable=False)
    num_relations = db.Column(db.Integer, nullable=False)
    max_gap = db.Column(db.Integer, nullable=False)
    max_tirp_length = db.Column(db.Integer, nullable=False)
    index_same = db.Column(db.Boolean, nullable=False)
    discretization_name = db.Column(
        db.String(150), db.ForeignKey("discretization.id"), nullable=False
    )


class Visualization(db.Model):
    """
    This table holds all the info about the dataSet that are ready to visualize
    Authors: Roi Omer Yiftah
    """

    id = db.Column(db.String(50), primary_key=True)
    dataset = db.Column(db.String(150), db.ForeignKey("info_about_datasets.Name"))
    run = db.Column(db.String(150), db.ForeignKey("run.id"), nullable=False)
    KL_id = db.Column(db.String(150), db.ForeignKey("karma_lego.id"), nullable=True)
