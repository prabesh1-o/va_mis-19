import base64
import json

from odoo import http
from odoo.http import request


class CarouselController(http.Controller):
    @http.route(
        "/mis/carousel", methods=["GET"], auth="public", type="http", csrf="false"
    )
    def get_carousel_data(self):
        try:
            carousels = request.env["mis.carousel.manager"].search(
                [], order="sequence ASC"
            )
            result = []
            for carousel in carousels:
                if carousel.image:
                    base64.b64encode(carousel.image).decode("utf-8")

                result.append(
                    {
                        "id": carousel.id,
                        "title": carousel.name,
                        "content": carousel.content,
                        "image_url": carousel.image_url,
                        "sequence": carousel.sequence,
                    }
                )
            return json.dumps({"success": True, "data": result, "count": len(result),})
        except Exception as e:
            return {"success": False, "error": str(e)}
