from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm


class Report:
    def __init__(self, output_path, pagesize=A4, margins=20 * mm):
        """
        Initialize a new report.

        :param output_path: Path where the PDF will be saved
        :param pagesize: Page size (default: A4)
        :param margins: Margins in mm (default: 20mm)
        """
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=pagesize,
            rightMargin=margins,
            leftMargin=margins,
            topMargin=margins,
            bottomMargin=margins,
        )
        self.story = []
        self.styles = getSampleStyleSheet()

        # Define common styles
        self.title_style = ParagraphStyle(
            "TitleStyle",
            parent=self.styles["Heading1"],
            alignment=1,  # TA_CENTER
            spaceAfter=12,
        )
        self.header_style = ParagraphStyle(
            "HeaderStyle",
            parent=self.styles["Heading2"],
            alignment=0,  # TA_LEFT
            spaceAfter=4,
            textColor=HexColor("#2E4053"),
        )
        self.body_style = ParagraphStyle(
            "BodyStyle",
            parent=self.styles["BodyText"],
            alignment=0,  # TA_LEFT
            firstLineIndent=0,  # Removed the indentation
            spaceAfter=8,
        )
        self.result_style = ParagraphStyle(
            "ResultStyle",
            parent=self.styles["BodyText"],
            alignment=0,  # TA_LEFT
            spaceAfter=6,
        )

    def add_title(self, title_text):
        """Add a title to the report."""
        self.story.append(Paragraph(title_text, self.title_style))

    def add_spacer(self, height=10 * mm):
        """Add vertical space to the report."""
        self.story.append(Spacer(1, height))

    def add_text(self, text, style=None):
        """Add text with specified style to the report."""
        if style is None:
            style = self.styles["Normal"]
        self.story.append(Paragraph(text, style))

    def add_paragraph(self, text, style=None):
        """Add a paragraph to the report."""
        if style is None:
            style = self.body_style

        # Simple newline replacement for proper PDF rendering
        if isinstance(text, str):
            formatted_text = text.replace("\n", "<br/>")
        else:
            formatted_text = text

        self.story.append(Paragraph(formatted_text, style))

    def add_header(self, text):
        """Add a header to the report."""
        self.story.append(Paragraph(text, self.header_style))

    def add_result(self, result, label, color):
        """Add a result indicator with icon and label."""
        self.story.append(
            Paragraph(
                f'<font color="{color}">{result} {label}</font>', self.result_style
            )
        )

    def add_success(self, label):
        self.add_result("✓", label, "#27AE60")

    def add_failure(self, label):
        self.add_result("✗", label, "#E74C3C")

    def add_separator(self):
        """Add a horizontal separator line."""
        self.story.append(Spacer(1, 2 * mm))
        self.story.append(
            HRFlowable(width="100%", thickness=0.5, color=HexColor("#808080"))
        )
        self.story.append(Spacer(1, 4 * mm))

    def add_page_break(self):
        """Add a page break to the report."""
        self.story.append(PageBreak())

    def generate_pdf(self):
        """Generate the PDF file."""
        self.doc.build(self.story)
        print(f"Report written to {self.output_path}")


if __name__ == "__main__":
    # Create a comprehensive example report using all available functions
    report = Report("example_report.pdf")

    report.add_title("Prüfkriterium 1: Name von Prüfkriterium 1")

    report.add_paragraph("<b>Erklärung:</b> Erklärung von Prüfkriterium 1")

    report.add_paragraph("<b>Auswertung:</b> Auswertung von Prüfkriterium 1")

    report.add_result("✓", "Item 1", "#27AE60")
    report.add_result("✓", "Item 2", "#27AE60")
    report.add_result("✗", "Item 3", "#E74C3C")
    report.add_result("✗", "Item 4", "#E74C3C")

    report.add_separator()

    report.add_title("Prüfkriterium 2: Name von Prüfkriterium 2")

    report.add_paragraph("<b>Erklärung:</b> Erklärung von Prüfkriterium 2")

    report.add_paragraph("<b>Auswertung:</b> Auswertung von Prüfkriterium 2")

    report.add_result("✓", "Item 1", "#27AE60")
    report.add_result("✓", "Item 2", "#27AE60")
    report.add_result("✗", "Item 3", "#E74C3C")
    report.add_result("✗", "Item 4", "#E74C3C")

    # Generate the final PDF
    report.generate_pdf()
