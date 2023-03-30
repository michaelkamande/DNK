from .models import Enterprise


class Check:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request): 
		response = self.get_response(request)
		return response

	def process_view(self, request, view_func, *view_args, **view_kargs):
		request.exp = None
		ent = None
		if Enterprise.objects.filter(id=1).exists():
			ent = Enterprise.objects.get(id=1)
			request.exp = ent.check_status
