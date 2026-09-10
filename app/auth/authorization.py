PERMISSIONS = {
    "manage_products": "Gestionar productos e inventario",
    "manage_customers": "Gestionar clientes",
    "manage_company": "Modificar la configuración de empresa",
    "manage_users": "Gestionar usuarios y roles",
    "manage_cash": "Gestionar caja y movimientos de efectivo",
    "view_reports": "Consultar reportes y auditoría",
    "create_invoices": "Crear y confirmar facturas",
}

ROLE_PERMISSIONS = {
    "Administrador": set(PERMISSIONS),
    "Vendedor": {"create_invoices", "manage_customers"},
    "Cajero": {"create_invoices", "manage_cash"},
    "Contador": {"view_reports"},
}


def can(role: str | None, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role or "", set())
