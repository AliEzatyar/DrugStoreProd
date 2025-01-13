from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path("", views.main_page, name="main"),
    path("search/home/<str:term>", views.main_page, name="main_search"),
    path("search/<str:type_>", views.search, name="search"),
    path("buy", views.buy, name="bgt"),
    path("sell/<int:id>", views.sell, name="sld"),
    path("read-qr/", views.read_qr_sell, name="sldqr"),
    # js
    path("listAll/", views.all_drugs, name="get_all_drugs"),  # in js
    path("listBgts/", views.get_drug_bgts, name="get_bgts"),  # in js
    path("getCompanies/", views.get_drug_companies, name="get_companies"),  # in js
    path("photo/", views.send_sld_photo, name="send_sld_photo"),
    # show details
    path(
        "detail/<str:name>/<str:company>/",
        views.show_drug_detail,
        name="show_drug_detail",
    ),
    path(
        "bgt_detail/<str:name>/<str:company>/<str:date>/",
        views.show_bgt_detail,
        name="show_bgt_detail",
    ),
    path(
        "sld_detail/<str:name>/<str:company>/<str:date>/<str:customer>/",
        views.show_sld_detail,
        name="show_sld_detail",
    ),
    # editing
    path(
        "Bgtdit/<str:name>/<str:company>/<str:date>/", views.edit_bgt, name="edit_bgt"
    ),
    path(
        "SldEdit/<str:name>/<str:company>/<str:date>/<str:customer>",
        views.edit_sld,
        name="edit_sld",
    ),
    # deleting
    path("delete-drug/<str:name>/<str:company>/", views.delete, name="delete_drug"),
    path(
        "delete-bgt/<str:name>/<str:company>/<str:date>/",
        views.delete,
        name="delete_bgt",
    ),
    path(
        "delete-sld/<str:name>/<str:company>/<str:date>/<str:customer>/",
        views.delete,
        name="delete_sld",
    ),
    # show lists of sales and purchases
    path("list/<str:list_type>/", views.show_list, name="show_list"),
    path(
        "search/list/<str:list_type>/<str:term>",
        views.show_list,
        name="show_list_search",
    ),
    # show the list for a specifc drug or company
    path("show-specific/<str:list_type>/", views.show_specific, name="show_specific"),
    # show the list for a specific bill
    path("list/bill/<str:list_type>/", views.show_list, name="show_list_bill"),
    # finance
    path("sld/profits", views.balance, name="profs"),
    # notes
    path("notes/all", views.NotesList.as_view(), name="notes_list_all"),
    path("notes/<int:page>/", views.NotesList.as_view(), name="notes_list_partial"),
    path("notes/create", views.CreateNote.as_view(), name="create_note"),
    path("notes/<int:pk>/update", views.UpdateNote.as_view(), name="update_note"),
    path("notes/delete", views.delete_note, name="delete_notes"),
    # loan
    path("loan/create", views.manage_loan, name="create_loan"),
    path("loan/<int:id>/update", views.manage_loan, name="update_loan"),
    path("loan/list", views.list_loans, name="list_loans"),
    path("__logs__/",views.read_logs,name="read_logs")
    #
]
