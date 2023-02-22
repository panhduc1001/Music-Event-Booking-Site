from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from .forms import BookingForm, FilterForm, CommentForm
from .models import Event, Comment, Booking
from . import db

bp = Blueprint("findevents", __name__, url_prefix="/findevents")


@bp.route("/", methods=["GET", "POST"])
def show():
    """
    Renders the findevents page.
    Will use URL parameters to filter events.
    """
    error = None
    query = Event.query
    specified_after_date = False

    # URL parameter filters, ignore the "submit" key in arguments
    for key in request.args.keys():
        if request.args[key] != "" and request.args[key] != "submit":
            if key == "title":
                title = "%" + request.args["title"] + "%"
                query = query.filter(Event.title.ilike(title))

            if key == "artist":
                artist = "%" + request.args["artist"] + "%"
                query = query.filter(Event.artist.ilike(artist))

            if key == "genre":
                genre = "%" + request.args["genre"] + "%"
                query = query.filter(Event.genre.ilike(genre))

            if key == "aftertimestamp":
                aftertimestamp = request.args["aftertimestamp"]
                query = query.filter(Event.timestamp >= aftertimestamp)
                specified_after_date = True

            if key == "beforetimestamp":
                beforetimestamp = request.args["beforetimestamp"]
                query = query.filter(Event.timestamp <= beforetimestamp)

            # If a the status is booked or upcoming, check the number of available tickets
            if key == "status":
                status = request.args["status"]
                if status == "booked":
                    query = query.filter(Event.status.like("upcoming"))
                    query = query.filter(Event.tickets == 0)
                elif status == "upcoming":
                    query = query.filter(Event.status.like("upcoming"))
                    query = query.filter(Event.tickets != 0)
                else:
                    query = query.filter(Event.status.like(status))

    # If the timestampafter is left empty, it will only show upcoming events
    # if not specified_after_date:
    #     query = query.filter(Event.timestamp >= datetime.now())

    # Limit search result to 10, and sort by timestamp
    events = query.order_by(Event.timestamp.asc()).limit(10).all()

    # Flash an error if the query returns no results
    if events == []:
        error = "No events found"
    else:
        # If the status is upcoming, but there are no tickets available, set the status display to booked
        for event in events:
            if event.tickets == 0 and event.status == "upcoming":
                setattr(event, "status_display", "booked")
            else:
                setattr(event, "status_display", event.status)

    filterform = FilterForm()

    if error is None:
        return render_template(
            "pages/findevents.jinja",
            events=enumerate(events),
            filterform=filterform,
            request=request,
        )
    else:
        flash(error)

    return render_template(
        "pages/findevents.jinja",
        events=enumerate(events),
        filterform=filterform,
        request=request,
    )


@bp.route("/<id>", methods=["GET", "POST"])
def details(id):
    """
    Renders the eventdetails page.
    """
    error = None
    event = Event.query.get(id)

    # If event cannot be found by the id, return 404 not found
    if event == None:
        abort(404)
    else:
        # If the status is upcoming, but there are no tickets available, set the status display to booked
        if event.tickets == 0 and event.status == "upcoming":
            setattr(event, "status_display", "booked")
        else:
            setattr(event, "status_display", event.status)

        commentform = CommentForm()
        bookingform = BookingForm()

        if commentform.validate_on_submit():
            add_comment(commentform)
            return redirect(url_for("findevents.details", id=id))

        if bookingform.validate_on_submit():
            add_booking(bookingform)
            return redirect(url_for("findevents.details", id=id))

    if error:
        flash(error)

    return render_template(
        "pages/eventdetails.jinja",
        event=event,
        commentform=commentform,
        bookingform=bookingform,
    )


@login_required
def add_comment(commentform):
    """
    Adds a comment to the database.
    Requires the user to be logged in.
    """
    event_id = commentform.event_id.data
    comment = Comment(
        desc=commentform.desc.data,
        event_id=event_id,
        user_id=current_user.id,
        username=current_user.username,
    )

    db.session.add(comment)
    db.session.commit()


@login_required
def add_booking(bookingform):
    """
    Adds a booking to the database.
    Requires the user to be logged in.
    """
    tickets = bookingform.tickets.data
    price = bookingform.price.data
    event_id = bookingform.event_id.data
    event = Event.query.get(event_id)

    # If the number of tickets booked exceeds the remaining number of tickets, flash an error
    # Else remove the tickets from event tickets, create a booking object, and commit add it to the database
    if tickets > event.tickets:
        error = "Booking denied: Exceeded number of tickets available"
        flash(error)
    else:
        booking = Booking(
            tickets=tickets,
            price=price,
            event_id=event_id,
            user_id=current_user.id,
        )
        event.tickets = event.tickets - tickets
        db.session.add(booking)
        db.session.commit()
