function email(t, d, u) {
	var email = u + '@' + d + '.' + t;
	document.write('<a href="mailto:' + email + '">' + email + '</a>');
}