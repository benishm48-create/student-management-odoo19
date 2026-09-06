FROM odoo:19.0

USER root

COPY . /mnt/extra-addons/students_management

RUN chown -R odoo:odoo /mnt/extra-addons/students_management

USER odoo

CMD ["CMD ["/mnt/extra-addons/students_management/render-start.sh"]"]
