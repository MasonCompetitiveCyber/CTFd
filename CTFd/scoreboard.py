from flask import Blueprint, render_template

from CTFd.utils import config
from CTFd.utils.config.visibility import scores_visible
from CTFd.utils.decorators.visibility import check_score_visibility
from CTFd.utils.helpers import get_infos
from CTFd.utils.scores import get_standings
from CTFd.utils.user import is_admin, get_current_user
from CTFd.utils.dates import ctf_ended

scoreboard = Blueprint("scoreboard", __name__)


@scoreboard.route("/scoreboard")
@check_score_visibility
def listing():
    infos = get_infos()

    if config.is_scoreboard_frozen():
        infos.append("Scoreboard has been frozen")

    if is_admin() is True and scores_visible() is False:
        infos.append("Scores are not currently visible to users")

    standings = get_standings()
    user = get_current_user()
    return render_template("scoreboard.html", standings=standings, ctf_ended=ctf_ended(), hidden=user.team.hidden, infos=infos)


@scoreboard.route("/scoreboard-all")
@check_score_visibility
def listing_hidden():
    infos = get_infos()

    if config.is_scoreboard_frozen():
        infos.append("Scoreboard has been frozen")

    if is_admin() is True and scores_visible() is False:
        infos.append("Scores are not currently visible to users")

    standings = get_standings(hidden=True)
    return render_template("scoreboard_all.html", standings=standings, ctf_ended=ctf_ended(), infos=infos)
