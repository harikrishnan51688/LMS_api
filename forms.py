from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, URL, Email, NumberRange, Length
from flask_wtf.file import FileRequired, FileField, FileAllowed 


class RegisterForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=8, max=25, message='Password must be between 8 and 20 characters long')])
    name = StringField(label='Name', validators=[DataRequired()])
    submit = SubmitField(label='Sign up')

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Login")

class FileUpload(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    subtitle = StringField(label="Subtitle", validators=[DataRequired()])
    genre = StringField(label="Genre", validators=[DataRequired()])
    pages = IntegerField(label="No of pages", validators=[DataRequired(), NumberRange(min=1)])
    author = StringField(label="Author", validators=[DataRequired()])
    price = DecimalField(label="Price", validators=[DataRequired(), NumberRange(min=1)])
    file = FileField(label="File upload", validators=[FileRequired(), FileAllowed(['pdf'], 'Only PDF files are allowed!')])
    image = FileField(label="Image", validators=[FileRequired(), FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField(label="Submit")

class EditBook(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    subtitle = StringField(label="Subtitle", validators=[DataRequired()])
    genre = StringField(label="Genre", validators=[DataRequired()])
    pages = IntegerField(label="No of pages", validators=[DataRequired(), NumberRange(min=1)])
    author = StringField(label="Author", validators=[DataRequired()])
    price = DecimalField(label="Price", validators=[DataRequired(), NumberRange(min=1)])
    file = FileField(label="File upload", validators=[FileAllowed(['pdf'], 'Only PDF files are allowed!')])
    image = FileField(label="Image", validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField(label="Submit")

class SectionForm(FlaskForm):
    section_name = StringField(label='Section name', validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class SearchForm(FlaskForm):
    text = StringField(label="Search", validators=[DataRequired()])

class RatingForm(FlaskForm):
    comment = StringField(label="Comment", validators=[DataRequired()])
    rating = SelectField('Rating', choices=[(str(x), str(x)) for x in range(1, 6)], validators=[DataRequired()])
    submit = SubmitField('Submit')