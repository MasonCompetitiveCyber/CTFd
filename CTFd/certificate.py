from io import BytesIO 

from flask import Blueprint, send_file, abort, request
from PIL import Image, ImageFont, ImageDraw

from CTFd.utils import config
from CTFd.utils.decorators import require_team
from CTFd.utils.scores import get_standings
from CTFd.utils.user import get_current_user, get_team_place
from CTFd.utils.dates import ctf_ended

certificate = Blueprint("certificate", __name__)

y_offset = 450

def draw_text(draw, img_width, font, size, text, color, custom_offset=0):
    global y_offset

    font = ImageFont.truetype(font, size)
    _, descent = font.getmetrics()
    text_height = font.getmask(text).getbbox()[3] + descent
    text_width = font.getmask(text).getbbox()[2]
    x = (img_width//2) - (text_width//2)
    y = y_offset + custom_offset
    draw.text((x, y), text, font=font, fill=color) 
    y_offset = y + text_height

@certificate.route("/certificate")
@require_team
def download_cert():
    if ctf_ended():
        global y_offset

        user = get_current_user()
        user_name = f"[{user.name}]"
        team_name = user.team.name

        if request.args['certButton'] == "student" and not user.hidden:
            standings = get_standings(hidden=False)
            type_text = "[student teams]"
            filename = "pctf-cert-student.png"
        elif request.args['certButton'] == "all":
            standings = get_standings(hidden=True)
            type_text = "[all teams]"
            filename = "pctf-cert-all.png"
        else:
            error = "Unauthorized: You are not on a student team!"
            abort(401, description=error)
            
        pos = f"Placed {get_team_place(user.team.id)}/{len(standings)}"

        cert_img = Image.open('CTFd/themes/pctf/static/img/pctf_cert.png') 
        img_width, _ = cert_img.size
        draw = ImageDraw.Draw(cert_img) 
        y_offset = 450

        draw_text(draw, img_width, 'CTFd/themes/pctf/assets/css/cascadiacode/font/CascadiaMono-Regular.ttf', 125, team_name, "gold")
        draw_text(draw, img_width, 'CTFd/themes/pctf/assets/css/cascadiacode/font/CascadiaMono-Light.ttf', 50, user_name, "white", 10)
        draw_text(draw, img_width, 'CTFd/themes/pctf/assets/css/cascadiacode/font/CascadiaMono-SemiLight.ttf', 70, pos, "gold", 50)
        draw_text(draw, img_width, 'CTFd/themes/pctf/assets/css/cascadiacode/font/CascadiaMono-Light.ttf', 50, type_text, "white")
        
        img_io = BytesIO()
        cert_img.save(img_io, 'PNG', quality=70)
        img_io.seek(0)
        return send_file(img_io, mimetype='cert_img/png', attachment_filename=filename, as_attachment=True)
    else:
        error = "{} has not ended yet".format(config.ctf_name())
        abort(403, description=error)