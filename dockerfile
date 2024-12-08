FROM odoo:17.0

USER root

# Install Python packages
RUN pip3 install PyJWT

USER odoo
