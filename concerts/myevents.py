from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from datetime import datetime
import os
from base64 import b64encode
import base64

from .forms import EventForm
from .models import Booking, Event
from . import db

bp = Blueprint("myevents", __name__, url_prefix="/myevents")


@bp.route("/", methods=["GET", "POST"])
@login_required
def show():
    """
    Renders the myevents page by querying events with the current user's id.
    Requires the user to be logged in.
    """
    error = None
    events = current_user.events
    events.sort(key=lambda event: event.id, reverse=True)
    if events == []:
        error = "No events found"

    for event in events:
        # HTML datetime-local input has a different formatting to python
        setattr(event, "timestampformatted", event.timestamp.strftime("%Y-%m-%dT%H:%M"))

        # If the status is upcoming, but there are no tickets available, set the status display to booked
        if event.tickets == 0 and event.status == "upcoming":
            setattr(event, "status_display", "booked")
        else:
            setattr(event, "status_display", event.status)

    eventform = EventForm()

    if eventform.validate_on_submit():
        # If the event already exists, update instead of creating a new event
        if eval(eventform.event_id.data):
            update_event(eventform)
            return redirect(url_for("myevents.show"))
        else:
            # If the user tries to create an event in the past, return an error
            localdate = datetime.now()
            eventdate = datetime.strptime(eventform.timestamp.data, "%Y-%m-%dT%H:%M")
            if eventdate < localdate:
                error = "Cannot create an event in the past"
            else:
                add_event(eventform)
                return redirect(url_for("myevents.show"))

    if error:
        flash(error)

    return render_template(
        "pages/myevents.jinja",
        events=enumerate(events),
        eventform=eventform,
    )


@bp.route("/delete/<event_id>", methods=["GET", "POST"])
@login_required
def delete(event_id):
    """
    Calls delete event function.
    Requires the user to be logged in.
    """
    delete_event(event_id)
    flash("Successfully deleted event")
    return redirect(url_for("myevents.show"))


def check_upload_file(eventform):
    """
    Uploads a file from form to database and return its upload path.
    If there is no input file and the event already exists, return the existing event's image upload path.
    If there is no input file and no existing event, return the default image upload path.
    """
    file = eventform.image.data
    print("CHECKING UPLOADED FILE")
    print(file)
    event_id = eventform.event_id.data

    if file:
        image_data = file.read()
        image_render = base64.b64encode(image_data).decode("ascii")

        return [image_data, image_render]

    elif event_id:
        event = Event.query.get(event_id)
        return [event.image_data, event.image_render]

    else:
        flash("No image was found")
        return ["", ""]


@login_required
def add_event(eventform):
    """
    Adds an event to the database.
    Requires the user to be logged in.
    """
    [image_data, image_render] = check_upload_file(eventform)
    timestamp = datetime.strptime(eventform.timestamp.data, "%Y-%m-%dT%H:%M")

    event = Event(
        timestamp=timestamp,
        title=eventform.title.data,
        artist=eventform.artist.data,
        genre=eventform.genre.data,
        venue_name=eventform.venue_name.data,
        venue_address=eventform.venue_address.data,
        status=eventform.status.data,
        desc=eventform.desc.data,
        tickets=eventform.tickets.data,
        price=eventform.price.data,
        image_data=image_data,
        image_render=image_render,
        user_id=current_user.id,
    )

    db.session.add(event)
    db.session.commit()


@login_required
def update_event(eventform):
    """
    Updates an event on the database.
    Requires the user to be logged in.
    """
    event = Event.query.get(eventform.event_id.data)

    image = check_upload_file(eventform)
    timestamp = datetime.strptime(eventform.timestamp.data, "%Y-%m-%dT%H:%M")

    event.timestamp = timestamp
    event.title = eventform.title.data
    event.artist = eventform.artist.data
    event.genre = eventform.genre.data
    event.venue_name = eventform.venue_name.data
    event.venue_address = eventform.venue_address.data
    event.status = eventform.status.data
    event.desc = eventform.desc.data
    event.tickets = eventform.tickets.data
    event.price = eventform.price.data
    event.image = image
    event.user_id = current_user.id

    db.session.commit()


@login_required
def delete_event(event_id):
    """
    Delete an event on the database.
    Requires the user to be logged in.
    """
    event = Event.query.get(event_id)
    bookings = Booking.query.filter(Booking.event_id == event_id).all()
    for booking in bookings:
        db.session.delete(booking)
    db.session.delete(event)
    db.session.commit()
