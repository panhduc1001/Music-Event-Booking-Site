from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user

from .models import Event

bp = Blueprint("bookedevents", __name__, url_prefix="/bookedevents")


@bp.route("/", methods=["GET", "POST"])
@login_required
def show():
    """
    Renders the bookedevents page by querying bookings with the current user's id.
    Requires the user to be logged in.
    """
    error = None
    bookings = current_user.bookings

    # Check if current_user has any bookings
    if bookings == []:
        error = "No bookings found"
    else:
        for booking in bookings:
            # Get an event by its id, and attach it to the booking object
            # This is required since a booking only has a booking_id attribute
            event = Event.query.get(booking.event_id)
            setattr(booking, "event", event)

            # If the status is upcoming, but there are no tickets available, set the status display to booked
            if event.tickets == 0 and event.status == "upcoming":
                setattr(event, "status_display", "booked")
            else:
                setattr(event, "status_display", event.status)

    if error:
        flash(error)

    return render_template(
        "pages/bookedevents.jinja",
        bookings=enumerate(bookings),
    )
