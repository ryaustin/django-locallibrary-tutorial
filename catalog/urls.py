from django.urls import path

from catalog.integrations.zoho_books import zoho_views

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>',
         views.AuthorDetailView.as_view(), name='author-detail'),
]


urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),  # Added for challenge
]


# Add URLConf for librarian to renew a book.
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]


# Add URLConf to create, update, and delete authors
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
]

# Add URLConf to create, update, and delete books
urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]

# Add URLConf for book store
urlpatterns += [
    path('store/', views.book_store, name='store'),
    path('store/<use_htmx>', views.book_store, name='store'),
    path('store/book/add/<book_id>', views.add_to_cart, name='add-to-cart'),
    path('store/book/add/<book_id>/<go_to_cart>', views.add_to_cart, name='add-to-cart'),
    path('store/book/add/<book_id>/<go_to_cart>/<use_htmx>', views.add_to_cart, name='add-to-cart'),
    path('store/book/remove/<book_id>', views.remove_from_cart, name='remove-from-cart'),
    path('store/book/remove/<book_id>/<use_htmx>', views.remove_from_cart, name='remove-from-cart'),
    path('store/clear_cart/', views.clear_cart, name='clear-cart'),
    path('store/clear_cart/<use_htmx>', views.clear_cart, name='clear-cart'),
    path('store/cart_detail/<cart_id>', views.cart_detail, name='cart-detail'),
    path('store/cart_detail/<cart_id>/<use_htmx>', views.cart_detail, name='cart-detail'),

    # Patterns for partials
    path('store/book_details/<book_id>', views.book_detail_partial, name='book-detail-partial'),
    path('store/cart_button_partial/<cart_id>', views.cart_button_info_partial, name='cart-button-partial'),
    path('store/cart_total_row_partial/<cart_id>', views.cart_total_row_partial, name='cart-total-row'),

]

# Integrations
urlpatterns += [
    path('integrations', views.integrations_view, name='integrations'),
    # zoho books
    path('zoho/callback', zoho_views.zoho_books_callback, name='zoho-books-callback'),
    path('zoho/connect', zoho_views.connect_to_zoho_books, name='connect-to-zoho-books'),
    path('zoho/disconnect', zoho_views.disconnect_from_zoho_books, name='disconnect-from-zoho-books'),
]