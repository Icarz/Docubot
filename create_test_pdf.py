from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("sample_policy.pdf", pagesize=letter)
c.drawString(50, 750, "REFUND AND RETURN POLICY")
c.drawString(50, 720, "Section 3.1: Refund Window")
c.drawString(50, 700, "All purchases are eligible for refund or return within 30 days of purchase.")
c.drawString(50, 680, "Items must be in original condition with all packaging intact.")
c.drawString(50, 660, "Section 3.2: Shipping Costs")
c.drawString(50, 640, "Original shipping costs are non-refundable. Return shipping is the responsibility")
c.drawString(50, 620, "of the customer unless the return is due to a defect.")
c.save()
print("Created sample_policy.pdf")