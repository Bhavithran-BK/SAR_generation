from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

class TemplateEngine:
    def __init__(self, template_dir: str = "app/templates"):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.env.filters["currency"] = self.format_currency

    def format_currency(self, value, currency_symbol="₹"):
        # Basic formatter. For INR Lakhs/Crores, a more complex one is needed.
        # This is a placeholder for standard formatting.
        return f"{currency_symbol}{value:,.2f}"

    def render(self, template_name: str, context: dict) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)

# Singleton
template_engine = TemplateEngine()
