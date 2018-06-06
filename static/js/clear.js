function prev(x){do{x=x.previousSibling;}while(x&&x.nodeType==3)return x;}
function next(x){do{x=x.nextSibling;}while(x&&x.nodeType==3)return x;}
function showClose(v){
	if(v.value.length){
		next(v).style.display = '';
	}
	else{
		next(v).style.display = 'none';
	}
}