# vim: et:sta:bs=2:sw=4:
# todo: add localization
def humanized_enum (it, normal_sep=u", ", final_sep=u" en "):
	lst = list(it)
	if len(lst)==0:
		return ""
	if len(lst)==1:
		return lst[0]
	return final_sep.join([normal_sep.join(lst[0:-1]),lst[-1]])