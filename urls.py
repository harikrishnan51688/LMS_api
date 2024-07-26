from flask_restful import Api
from api import *

api = Api()

# ---------------- API -----------------------
# Login
api.add_resource(Login_, '/api/login')
api.add_resource(CheckAuth, '/api/check-auth')
api.add_resource(CreateAccount, '/api/register')

# Search
api.add_resource(SearchBooks, '/api/search')
api.add_resource(SearchTags, '/api/searchtags')

# Profile
api.add_resource(Profile, '/api/profile')
api.add_resource(IsBorrowed, '/api/profile/isborrowed')
api.add_resource(ToggleExpiry, '/api/profile/toggle-expiry')
api.add_resource(RequestData, '/api/profile/request-data')
api.add_resource(DownloadData, '/api/profile/download-data')

 ## For Request, cancel, return, approve
api.add_resource(ReqBook, '/api/profile/requestbook')
api.add_resource(RetBook, '/api/profile/returnbook')
api.add_resource(CancelRequest, '/api/admin/cancelrequest')
api.add_resource(RemoveUser, '/api/admin/removeuser')
api.add_resource(ApproveRequest, '/api/admin/approve-request')
api.add_resource(BooksNotInSection, '/api/section/remaining-books')
api.add_resource(GrantBook, '/api/admin/grant-book')

# Admin dashboard
api.add_resource(Stats, '/api/admin/stats')
api.add_resource(AllUsers, '/api/admin/allusers')
api.add_resource(BookRequests, '/api/admin/book-requests')
api.add_resource(PurchaseData, '/api/admin/book-purchases')

# API for Books 
api.add_resource(Ebook_, '/api/book/all')
api.add_resource(Ebook_Byid, '/api/book/<int:book_id>')
api.add_resource(Create_Ebook, '/api/book/add-book')
api.add_resource(Update_Ebook, '/api/book/update-book/<int:book_id>')
api.add_resource(Delete_Ebook, '/api/book/delete-book')
api.add_resource(RateBook, '/api/book/submit-rating')
api.add_resource(DeleteRating, '/api/book/delete-rating')
api.add_resource(Ratings, '/api/book/ratings')
api.add_resource(BookPurchase, '/api/book/payment')
api.add_resource(IsPurchased, '/api/book/is_purchased')

# API for Sections
api.add_resource(Sections_, '/api/section/all')
api.add_resource(GetSection_byId, '/api/section/<int:section_id>')
api.add_resource(Create_Section, '/api/section/add-section')
api.add_resource(Update_Section, '/api/section/update-section/<int:section_id>')
api.add_resource(Delete_Section_, '/api/section/delete-section/<int:section_id>')
api.add_resource(AddBookToSection, '/api/section/add-book')
api.add_resource(RemoveBookFromSection, '/api/section/remove-book')

# API for chart
api.add_resource(Chart_Sections, '/api/chart/sections')
api.add_resource(UserJoinChart, '/api/chart/users')
api.add_resource(PaymentChart, '/api/chart/payment')
# ---------------------------