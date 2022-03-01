from multiprocessing import context
from operator import sub
from django.shortcuts import redirect, render
from django.contrib import messages

# Create your views here.

from .models import Book, Author, BookInstance, Genre, Cart


def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available copies of books
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits},
    )


from django.views import generic


class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Book


class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author


from django.contrib.auth.mixins import LoginRequiredMixin


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, permission_required

# from .forms import RenewBookForm
from catalog.forms import RenewBookForm


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


# Classes created for the forms challenge
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'

@login_required
def book_store(request, use_htmx=False):
    book_list = Book.objects.all()
    cart = get_cart(request)
    if not cart:
        make_cart(request)
        
    context = {
        'book_list' : book_list,
        'cart' : cart
    }
    if use_htmx == 'True':
        return render(request, 'store_htmx/htmx_book_store.html', context)
    return render(request, 'store_no_htmx/book_store.html', context)

@login_required
def make_cart(request):
    cart = Cart(owner=request.user).save()
    return cart

@login_required
def get_cart(request):
    cart = request.user.cart_set.all().last()
    return cart

def clear_cart(request, use_htmx=False):
    cart = get_cart(request)
    cart.items.clear()
    cart.save()
    if use_htmx == 'True':
            # return redirect('store', use_htmx=True)
            context = {'cart':cart,}
            response = render(request, 'store_htmx/htmx_cart_partial.html', context)
            response['HX-Trigger'] = "cart_updated"
            return response
    return redirect('store')

def add_to_cart(request, book_id, go_to_cart=False, use_htmx=False):
    cart = get_cart(request)
    book = Book.objects.get(id=book_id)
    try:
        cart.items[book.title]
    except KeyError:
        # If the key does not exsist we initialize it with 0
        cart.items[book.title] = 0
    cart.items[book.title] += 1
    cart.save()
    if not go_to_cart == 'True':
        if use_htmx == 'True':
            # return redirect('store', use_htmx=True)
            context = {'cart':cart}
            response = render(request, 'store_htmx/htmx_partial_cart_button.html', context)
            response['HX-Trigger'] = "cart_updated"
            return response
        else:
            return redirect('store')
    return redirect('cart-detail', cart.id) 

def remove_from_cart(request, book_id, use_htmx=False):
    cart = get_cart(request)
    book = Book.objects.get(id=book_id)
    title = book.title
    try:
        cart.items.pop(title)
    except KeyError:
        messages.error(request, f"Book: '{title}' is not in your cart")
        return redirect('store')
    cart.save()
    if use_htmx == 'True':
            # return redirect('store', use_htmx=True)
            context = {'cart':cart,}
            response = render(request, 'store_htmx/htmx_cart_total_row_partial.html', context)
            response['HX-Trigger'] = "cart_updated"
            return response
    messages.success(request, f"Book: '{title}' was removed from your cart")
    return redirect('cart-detail', cart.id)

def cart_detail(request, use_htmx=False, *args, **kwargs):
    cart = Cart.objects.get(pk=int(kwargs['cart_id']))
    book_list = []
    book_names = cart.items.keys()
    for _book in book_names:
        book = Book.objects.get(title=_book)
        price = book.price
        qty = cart.items[_book]
        subtotal = price * qty
        carted_book = {
            'book' : book,
            'qty' : qty,
            'subtotal' : subtotal
        }
        book_list.append(carted_book)
    context = { 'cart':cart, 'book_list' : book_list, }
    if use_htmx == 'True':
        return render(request, 'store_htmx/htmx_cart_partial.html', context)
    return render(request, 'store_no_htmx/cart_detail.html', context)

# PARTIALS
def book_detail_partial(request, book_id):
    book = Book.objects.get(id=book_id)
    context = { 'book' : book}
    return render(request, 'store_htmx/htmx_partial_book_detail.html', context)

def cart_button_info_partial(request, cart_id):
    cart = Cart.objects.get(id=cart_id)
    context = {'cart':cart}
    return render(request, 'store_htmx/htmx_partial_cart_button.html', context)

def cart_total_row_partial(request, cart_id):
    cart = Cart.objects.get(id=cart_id)
    context = {'cart':cart}
    return render(request, 'store_htmx/htmx_cart_total_row_partial.html', context)