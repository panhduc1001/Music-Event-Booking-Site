from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField
from wtforms.fields import FloatField, IntegerField, SelectField, HiddenField
from wtforms.validators import InputRequired, Email, EqualTo, NumberRange
from wtforms.fields.html5 import DateTimeField

IMAGE_FILE_FORMATS = {"jpg", "png", "jpeg"}
EVENT_STATUS = [
    "upcoming",
    "inactive",
    "cancelled",
]


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email("Enter a valid email")])
    password = PasswordField("Password", validators=[InputRequired("Enter a password")])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("Enter a username")])
    email = StringField("Email", validators=[Email("Enter a valid email")])
    password = PasswordField("Password", validators=[InputRequired("Enter a password")])
    confirm = PasswordField(
        "Confirm password",
        validators=[
            InputRequired("Enter the password again"),
            EqualTo("password", message="Passwords should match"),
        ],
    )
    contact = IntegerField(
        "Contact number", validators=[InputRequired("Enter your contact number")]
    )
    address = StringField(
        "Address", validators=[InputRequired("Enter your current address")]
    )
    submit = SubmitField("Register")


class EventForm(FlaskForm):
    title = StringField("Event title", validators=[InputRequired("Enter a title")])
    artist = StringField(
        "Artist name", validators=[InputRequired("Enter the name of the artist")]
    )
    genre = StringField("Genre", validators=[InputRequired("Enter the event genre")])
    timestamp = StringField(
        "Date and time",
        validators=[InputRequired("Enter a title")],
    )
    venue_name = StringField(
        "Venue name", validators=[InputRequired("Enter the venue name")]
    )
    venue_address = StringField(
        "Venue address", validators=[InputRequired("Enter the venue address")]
    )
    desc = TextAreaField(
        "Description", validators=[InputRequired("Enter a description")]
    )
    status = SelectField(
        "Status",
        choices=EVENT_STATUS,
    )
    image = FileField(
        "Image",
        validators=[
            FileAllowed(IMAGE_FILE_FORMATS, message="Images only!"),
        ],
    )
    tickets = IntegerField(
        "Available tickets",
        validators=[NumberRange(min=0, message="Enter a valid number of tickets")],
    )
    price = FloatField(
        "Ticket price ($AUD)",
        validators=[NumberRange(min=0, message="Enter a valid price")],
    )
    submit = SubmitField("Save changes")
    event_id = HiddenField("Event ID")


class CommentForm(FlaskForm):
    desc = TextAreaField(
        "Write a comment", validators=[InputRequired("Write a comment")]
    )
    submit = SubmitField("Comment")
    event_id = HiddenField("Event ID")


class BookingForm(FlaskForm):
    tickets = IntegerField(
        "Number of tickets",
        validators=[
            InputRequired("Enter the number of tickets to book"),
            NumberRange(min=0, message="Enter a valid number of tickets"),
        ],
    )
    submit = SubmitField("Confirm booking")
    price = HiddenField("Ticket price")
    event_id = HiddenField("Event ID")


class FilterForm(FlaskForm):
    title = StringField("Filter by title")
    artist = StringField("Filter by artist")
    genre = StringField("Filter by genre")

    aftertimestamp = DateTimeField("Search events after")
    beforetimestamp = DateTimeField("Search events before")
    status = SelectField("Filter by event status", choices=EVENT_STATUS)

    submit = SubmitField("Search")
