from odoo import api, fields, models

DEFAULT_IMAGE_URL = "https://geomate.com.np/web/image"


class MisCarouselManager(models.Model):
    _name = "mis.carousel.manager"
    _description = "Mis Carousel Manger"

    def _get_last_sequence(self):
        return self.search([], order="sequence DESC", limit=1).sequence + 1

    name = fields.Char(string="Carousel Name")
    sequence = fields.Integer(default=_get_last_sequence)
    content = fields.Text(string="Carousel Content")
    image = fields.Image(string="Carousel Image", required=True)
    image_url = fields.Char(
        string="Image URL", readonly=True, compute="_compute_image_url", store=True
    )

    @api.onchange("image")
    @api.depends("image")
    def _compute_image_url(self):
        for carousel in self:
            if not carousel.image:
                carousel.image_url = ""
            else:
                carousel.image_url = (
                    f"{DEFAULT_IMAGE_URL}/{carousel._name}/{carousel.id}/image"
                )
