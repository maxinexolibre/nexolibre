<#
  Crea la Lista de SharePoint "Catalogo de partes" con todas las columnas del catalogo,
  los desplegables y las columnas de "Publicar en...".

  Requisitos:
    1) Instalar el modulo PnP PowerShell (una sola vez):
         Install-Module PnP.PowerShell -Scope CurrentUser
    2) Editar $SiteUrl con la URL de tu sitio de SharePoint.
    3) Ejecutar:  pwsh ./Crear-Lista-SharePoint.ps1   (o desde Windows PowerShell)

  Los "InternalName" coinciden con las claves del catalogo (parts.json) para que
  el flujo de Power Automate los mapee directo.
#>

$SiteUrl  = "https://TU-TENANT.sharepoint.com/sites/Nexolibre"   # <-- EDITAR
$ListName = "Catalogo de partes"

Connect-PnPOnline -Url $SiteUrl -Interactive

$list = New-PnPList -Title $ListName -Template GenericList -OnQuickLaunch -ErrorAction Stop

# La columna "Title" integrada se usa como "Nombre"
Set-PnPField -List $ListName -Identity "Title" -Values @{ Title = "Nombre" } | Out-Null

# --- Texto ---
Add-PnPField -List $ListName -DisplayName "Ref (codigo)"      -InternalName "ref"               -Type Text -AddToDefaultView | Out-Null
Add-PnPField -List $ListName -DisplayName "Marca"             -InternalName "marca"             -Type Text -AddToDefaultView | Out-Null
Add-PnPField -List $ListName -DisplayName "Modelo compatible" -InternalName "modelo_compatible" -Type Text -AddToDefaultView | Out-Null
Add-PnPField -List $ListName -DisplayName "N de parte"        -InternalName "nro_parte"         -Type Text -AddToDefaultView | Out-Null
Add-PnPField -List $ListName -DisplayName "Garantia"          -InternalName "garantia"          -Type Text | Out-Null
Add-PnPField -List $ListName -DisplayName "Precio"            -InternalName "precio"            -Type Text | Out-Null
Add-PnPField -List $ListName -DisplayName "Imagen (archivo)"  -InternalName "imagen"            -Type Text | Out-Null

# --- Texto largo / URL ---
Add-PnPField -List $ListName -DisplayName "Descripcion"       -InternalName "descripcion"       -Type Note | Out-Null
Add-PnPField -List $ListName -DisplayName "Link externo"      -InternalName "link_externo"      -Type URL  | Out-Null

# --- Desplegables (Choice) ---
Add-PnPField -List $ListName -DisplayName "Categoria"     -InternalName "categoria"     -Type Choice -Choices "Bobina","Gradiente","RF","Fuente","Inyector","Tubo CT","Otro" -AddToDefaultView | Out-Null
Add-PnPField -List $ListName -DisplayName "Modalidad"     -InternalName "modalidad"     -Type Choice -Choices "MRI","CT","PET-CT" -AddToDefaultView | Out-Null
Add-PnPField -List $ListName -DisplayName "Estado"        -InternalName "estado"        -Type Choice -Choices "Recuperado y testeado","Nuevo","Para repuestos" | Out-Null
Add-PnPField -List $ListName -DisplayName "Disponibilidad" -InternalName "disponibilidad" -Type Choice -Choices "En stock","Bajo pedido","Reservado" -AddToDefaultView | Out-Null
Add-PnPField -List $ListName -DisplayName "Ubicacion"    -InternalName "ubicacion"     -Type Choice -Choices "Argentina","Chile","USA" -AddToDefaultView | Out-Null

# --- Publicar en... (Si/No) ---
Add-PnPField -List $ListName -DisplayName "Publicar en Web"    -InternalName "pub_web"    -Type Boolean -AddToDefaultView | Out-Null
Add-PnPField -List $ListName -DisplayName "Publicar en eBay"   -InternalName "pub_ebay"   -Type Boolean | Out-Null
Add-PnPField -List $ListName -DisplayName "Publicar en DOTmed" -InternalName "pub_dotmed" -Type Boolean | Out-Null

# --- (Opcional, para Fases 2-3: IDs que escribe la automatizacion) ---
# Add-PnPField -List $ListName -DisplayName "eBay listing id"   -InternalName "ebay_id"   -Type Text | Out-Null
# Add-PnPField -List $ListName -DisplayName "DOTmed listing id" -InternalName "dotmed_id" -Type Text | Out-Null

# Ref unico e indexado
Set-PnPField -List $ListName -Identity "ref" -Values @{ Indexed = $true; EnforceUniqueValues = $true } | Out-Null

# Defaults
Set-PnPField -List $ListName -Identity "pub_web"        -Values @{ DefaultValue = "1" } | Out-Null
Set-PnPField -List $ListName -Identity "disponibilidad" -Values @{ DefaultValue = "En stock" } | Out-Null

Write-Host "Lista '$ListName' creada en $SiteUrl" -ForegroundColor Green
