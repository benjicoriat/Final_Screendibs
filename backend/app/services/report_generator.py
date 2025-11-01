from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import json
import os
import tempfile
from typing import List, Dict
from ..core.config import settings
from ..models.payment import PlanType

class ReportGeneratorService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def setup_pdf_styles(self):
        """Creates custom PDF styles for elegant formatting."""
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(
            name='BookTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='AuthorName',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='ReportType',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=10,
            backColor=colors.HexColor('#ecf0f1')
        ))
        
        styles.add(ParagraphStyle(
            name='ElegantBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName='Helvetica',
            textColor=colors.HexColor('#2c2c2c')
        ))
        
        return styles
    
    def get_sections_for_plan(self, plan_type: PlanType) -> tuple:
        """Returns sections and plan name based on plan type."""
        if plan_type == PlanType.BASIC:
            sections = [
                ("Book Statistics", "Comprehensive numerical and factual data about the publication"),
                ("Synopsis", "Detailed plot summary and narrative overview"),
                ("Author Presentation", "Biographical information and literary career of the author"),
                ("Copyright and Publication Details", "Legal, publishing, and distribution information"),
                ("Past Adaptations", "Film, television, theater, and other media adaptations")
            ]
            plan_name = "Basic Literary Analysis"
            
        elif plan_type == PlanType.DETAILED:
            sections = [
                ("Book Statistics", "Comprehensive numerical and factual data about the publication"),
                ("Synopsis", "Detailed plot summary and narrative overview"),
                ("Author Presentation", "Biographical information and literary career of the author"),
                ("Copyright and Publication Details", "Legal, publishing, and distribution information"),
                ("Past Adaptations", "Film, television, theater, and other media adaptations"),
                ("Thematic and Symbolic Analysis", "Exploration of major themes, motifs, and symbolic elements"),
                ("Character and Setting Study", "In-depth analysis of characters, locations, and their significance"),
                ("Writing Style and Narrative Techniques", "Examination of prose style, narrative voice, and literary devices"),
                ("Impact and Legacy", "Cultural influence and lasting significance in literature"),
                ("Historical and Cultural Context", "Period context and sociocultural background of the work")
            ]
            plan_name = "Detailed Literary Analysis"
            
        elif plan_type == PlanType.PREMIUM:
            sections = [
                ("Book Statistics", "Comprehensive numerical and factual data about the publication"),
                ("Synopsis", "Detailed plot summary and narrative overview"),
                ("Author Presentation", "Biographical information and literary career of the author"),
                ("Copyright and Publication Details", "Legal, publishing, and distribution information"),
                ("Past Adaptations", "Film, television, theater, and other media adaptations"),
                ("Thematic and Symbolic Analysis", "Exploration of major themes, motifs, and symbolic elements"),
                ("Character and Setting Study", "In-depth analysis of characters, locations, and their significance"),
                ("Writing Style and Narrative Techniques", "Examination of prose style, narrative voice, and literary devices"),
                ("Impact and Legacy", "Cultural influence and lasting significance in literature"),
                ("Historical and Cultural Context", "Period context and sociocultural background of the work"),
                ("Critical Reception and Reviews", "Analysis of critical responses and scholarly interpretations"),
                ("Comparative Literature Study", "Connections to other works and literary traditions"),
                ("Psychological and Philosophical Interpretations", "Deeper meanings through psychological and philosophical lenses"),
                ("Symbolism and Allegorical Layers", "Hidden meanings and symbolic representations"),
                ("Reader Demographics and Audience Response", "Target audience analysis and reception patterns"),
                ("Marketing and Publication Strategy", "Commercial approach and market positioning"),
                ("Scholarly and Academic Analysis", "Academic discourse and research perspectives"),
                ("Influence on Other Media and Authors", "Impact on subsequent creative works and writers"),
                ("Future Prospects", "Potential sequels, reissues, and ongoing cultural relevance")
            ]
            plan_name = "Premium Literary Analysis"
        else:
            raise ValueError(f"Invalid plan type: {plan_type}")
        
        return sections, plan_name
    
    def generate_book_stats(self, book: str, author: str) -> List[Dict]:
        """Generates comprehensive book statistics."""
        prompt = f"""Generate exactly 10 important, specific statistics about "{book}" by {author}.

Provide factual information including:
- Publication year and original publisher
- Page count and word count (approximate)
- Genre and literary movement
- Awards and recognitions
- Sales figures or bestseller status
- Translation information
- Critical acclaim metrics
- Cultural impact indicators
- Adaptation details
- Reading level or target audience

Format as JSON array with EXACTLY this structure:
[
    {{"stat": "Publication Year", "value": "YYYY"}},
    {{"stat": "Original Publisher", "value": "Publisher Name"}},
    {{"stat": "Page Count", "value": "XXX pages"}},
    {{"stat": "Genre", "value": "Genre description"}},
    {{"stat": "Awards", "value": "Award details"}},
    {{"stat": "Sales", "value": "Sales information"}},
    {{"stat": "Translations", "value": "Translation details"}},
    {{"stat": "Critical Reception", "value": "Reception details"}},
    {{"stat": "Adaptations", "value": "Adaptation information"}},
    {{"stat": "Target Audience", "value": "Audience description"}}
]

Return ONLY valid JSON, no other text."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a meticulous literary researcher providing accurate book statistics. Return only valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            stats = json.loads(content)
            return stats
            
        except Exception as e:
            # Return default stats if API fails
            return [
                {"stat": "Publication Year", "value": "Information unavailable"},
                {"stat": "Original Publisher", "value": "Information unavailable"},
                {"stat": "Page Count", "value": "Information unavailable"},
                {"stat": "Genre", "value": "Information unavailable"},
                {"stat": "Awards", "value": "Information unavailable"},
                {"stat": "Sales", "value": "Information unavailable"},
                {"stat": "Translations", "value": "Information unavailable"},
                {"stat": "Critical Reception", "value": "Information unavailable"},
                {"stat": "Adaptations", "value": "Information unavailable"},
                {"stat": "Target Audience", "value": "Information unavailable"}
            ]
    
    def generate_section_content(self, book: str, author: str, section_name: str, section_description: str) -> str:
        """Generates content for a specific section."""
        prompt = f"""You are an erudite literary scholar with exceptional writing skills. Write a comprehensive, eloquent analysis for the following section about the book "{book}" by {author}.

SECTION: {section_name}
FOCUS: {section_description}

REQUIREMENTS:
- Write 6-8 substantial paragraphs (approximately 900-1200 words total)
- Each paragraph should be 4-7 sentences with rich detail
- Use sophisticated, varied vocabulary with precise literary terminology
- Maintain an elegant, scholarly tone throughout
- Structure each paragraph with clear topic sentences
- Include specific examples, quotes, and insights about the book
- Demonstrate deep literary analysis and critical thinking
- Ensure flawless grammar and syntax
- Make each paragraph substantive and interconnected
- Provide comprehensive coverage that fills a full page

Write ONLY the content, no titles or labels. Begin immediately with insightful analysis."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a distinguished literary critic and scholar known for eloquent, sophisticated prose and deep analytical insight."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"An error occurred while generating content for this section: {e}"
    
    def generate_report(self, book: str, author: str, plan_type: PlanType) -> str:
        """Generates a complete PDF report and returns the file path."""
        
        styles = self.setup_pdf_styles()
        sections, plan_name = self.get_sections_for_plan(plan_type)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        filename = temp_file.name
        temp_file.close()
        
        # Create PDF
        doc = SimpleDocTemplate(
            filename, 
            pagesize=letter, 
            topMargin=0.75*inch, 
            bottomMargin=0.75*inch
        )
        story = []
        
        # Title Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(book, styles['BookTitle']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"by {author}", styles['AuthorName']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(plan_name, styles['ReportType']))
        story.append(PageBreak())
        
        # Generate and add statistics
        stats = self.generate_book_stats(book, author)
        
        story.append(Paragraph("Book Statistics", styles['SectionTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        stat_data = [
            [
                Paragraph("<b>" + stat['stat'] + "</b>", styles['Normal']), 
                Paragraph(str(stat['value']), styles['Normal'])
            ] 
            for stat in stats
        ]
        
        stat_table = Table(stat_data, colWidths=[2.5*inch, 4*inch])
        stat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c2c2c')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        story.append(stat_table)
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph("Table of Contents", styles['SectionTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        toc_data = []
        for i, (section_name, _) in enumerate(sections, 1):
            toc_entry = f"{i}. {section_name}"
            toc_data.append([Paragraph(toc_entry, styles['Normal'])])
        
        toc_table = Table(toc_data, colWidths=[6*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(toc_table)
        story.append(PageBreak())
        
        # Generate content sections
        for section_name, section_description in sections:
            # Section title
            story.append(Paragraph(section_name, styles['SectionTitle']))
            story.append(Spacer(1, 0.3*inch))
            
            # Generate content
            content = self.generate_section_content(book, author, section_name, section_description)
            
            # Split into paragraphs and add to story
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['ElegantBody']))
                    story.append(Spacer(1, 0.15*inch))
            
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        return filename