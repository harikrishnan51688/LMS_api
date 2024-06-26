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
api.add_resource(IsBorrowed, '/api/isborrowed')
api.add_resource(ToggleExpiry, '/api/toggle-expiry')
api.add_resource(RequestData, '/api/request-data')
api.add_resource(DownloadData, '/api/download-data')

 ## For Request, cancel, return, approve
api.add_resource(ReqBook, '/api/requestbook')
api.add_resource(RetBook, '/api/returnbook')
api.add_resource(CancelRequest, '/api/cancelrequest')
api.add_resource(RemoveUser, '/api/removeuser')
api.add_resource(ApproveRequest, '/api/approve-request')
api.add_resource(BooksNotInSection, '/api/section/remaining-books')
api.add_resource(GrantBook, '/api/grant-book')

# Admin dashboard
api.add_resource(Stats, '/api/stats')
api.add_resource(AllUsers, '/api/allusers')
api.add_resource(BookRequests, '/api/book-requests')

# API for Books 
api.add_resource(Ebook_, '/api/books')
api.add_resource(Ebook_Byid, '/api/book/<int:book_id>')
api.add_resource(Create_Ebook, '/api/add-book')
api.add_resource(Update_Ebook, '/api/update-book/<int:book_id>')
api.add_resource(Delete_Ebook, '/api/delete-book')
api.add_resource(RateBook, '/api/submit-rating')
api.add_resource(DeleteRating, '/api/delete-rating')
api.add_resource(Ratings, '/api/ratings')

# API for Sections
api.add_resource(Sections_, '/api/sections')
api.add_resource(GetSection_byId, '/api/sections/<int:section_id>')
api.add_resource(Create_Section, '/api/add-section')
api.add_resource(Update_Section, '/api/update-section/<int:section_id>')
api.add_resource(Delete_Section_, '/api/delete-section/<int:section_id>')
api.add_resource(AddBookToSection, '/api/section/add-book')
api.add_resource(RemoveBookFromSection, '/api/section/remove-book')

# API for chart
api.add_resource(Chart_Sections, '/api/chart/sections')
api.add_resource(UserJoinChart, '/api/chart/users')
# ---------------------------