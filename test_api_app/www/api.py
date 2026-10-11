import json
import frappe
from frappe import _
from frappe.utils import validate_email_address

DOCTYPE = "Test Api"


# =====================================================================
# 1. CREATE API
# =====================================================================
@frappe.whitelist(methods=["POST"])
def create_test_api(name1=None, email=None):
    """
    Creates a new 'Test Api' record.
    
    Can be called via POST with form-data, x-www-form-urlencoded, or JSON payload:
    {
        "name1": "John Doe",
        "email": "john@example.com"
    }
    """
    # Fallback to JSON payload if parameters are not passed in query/form
    if not name1 and not email and frappe.request.data:
        try:
            data = frappe.parse_json(frappe.request.data)
            if isinstance(data, dict):
                name1 = data.get("name1")
                email = data.get("email")
        except Exception:
            pass

    # Basic validations
    if not name1:
        frappe.throw(_("Name (name1) is required"), frappe.MandatoryError)

    if email:
        validate_email_address(email, throw=True)

    # Permission check for creation
    if not frappe.has_permission(DOCTYPE, ptype="create"):
        frappe.throw(_("Not permitted to create {0}").format(DOCTYPE), frappe.PermissionError)

    # Create and insert document
    doc = frappe.get_doc({
        "doctype": DOCTYPE,
        "name1": name1,
        "email": email
    })
    doc.insert()

    return {
        "status": "success",
        "message": _("Record created successfully"),
        "data": doc.as_dict()
    }


# ==================================================================
# 2. GET SINGLE API
# ==================================================================
@frappe.whitelist(methods=["GET"])
def get_test_api(name):
    """
    Retrieves a single 'Test Api' document by ID/name.
    
    Query Params:
        name (str/int): The autoincrement ID/name of the record.
    """
    if not name:
        frappe.throw(_("Document 'name' (ID) is required"), frappe.MandatoryError)

    if not frappe.db.exists(DOCTYPE, name):
        frappe.throw(
            _("{0} with ID {1} not found").format(DOCTYPE, name),
            frappe.DoesNotExistError
        )

    doc = frappe.get_doc(DOCTYPE, name)

    # Permission check for reading
    doc.check_permission("read")

    return {
        "status": "success",
        "data": doc.as_dict()
    }


# =====================================================================
# 3. GET ALL API
# =====================================================================
@frappe.whitelist(methods=["GET"])
def get_all_test_api(fields=None, filters=None, limit_start=0, limit_page_length=50, order_by="modified desc"):
    """
    Retrieves a list of 'Test Api' records with pagination and filtering support.
    
    Query Params:
        fields (list/json string): Fields to fetch, e.g. ["name", "name1", "email"]
        filters (dict/list/json string): Filters, e.g. {"name1": ["like", "%John%"]}
        limit_start (int): Offset/start index (default: 0)
        limit_page_length (int): Page length (default: 50)
        order_by (str): Sort order (default: "modified desc")
    """
    # Permission check for reading
    if not frappe.has_permission(DOCTYPE, ptype="read"):
        frappe.throw(_("Not permitted to read {0}").format(DOCTYPE), frappe.PermissionError)

    # Parse JSON strings if passed as URL parameters
    if isinstance(fields, str):
        try:
            fields = json.loads(fields)
        except Exception:
            fields = [f.strip() for f in fields.split(",") if f.strip()]

    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except Exception:
            pass

    # Default fields if none specified
    if not fields:
        fields = ["name", "name1", "email", "creation", "modified"]

    records = frappe.get_list(
        doctype=DOCTYPE,
        fields=fields,
        filters=filters,
        start=int(limit_start or 0),
        page_length=int(limit_page_length or 50),
        order_by=order_by
    )

    total_count = frappe.db.count(DOCTYPE, filters=filters)

    return {
        "status": "success",
        "total_count": total_count,
        "limit_start": int(limit_start or 0),
        "limit_page_length": int(limit_page_length or 50),
        "data": records
    }