let updateBtns = document.getElementsByClassName('update-cart')

for(let i = 0; i < updateBtns.length; i++){
	updateBtns[i].addEventListener('click', function(){
		let itemId = this.dataset.item
		let action = this.dataset.action
		console.log(itemId, action)
		console.log(user)

		if(user === 'AnonymousUser'){
			console.log('Not logged in')
		} else {
			console.log('Logged in, sending data...')
		}
	})
}

