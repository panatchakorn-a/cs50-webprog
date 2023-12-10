from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from django.contrib import messages
from . import util
import random
import markdown2

class SearchForm(forms.Form):
    """to query searching"""
    keyword = forms.CharField(label="", widget=forms.TextInput(attrs={
        "class": "search",
        "placeholder": "Search by keyword"
    }))

class CreateForm(forms.Form):
    title = forms.CharField(label="Page Title", widget=forms.TextInput())
    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        "placeholder": "Fill Markdown content here"
    }))

class EditForm(forms.Form):
    edit_content = forms.CharField(label="", widget=forms.Textarea(attrs={
        "placeholder": "Edit your content here"
    }))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm(),
    })

def wiki(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html")
    
    content = markdown2.markdown(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content,
        "search_form": SearchForm(),
    })

def randomize(request):
    title = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse("encyclopedia:wiki", kwargs={"title": title}))

def search(request):
    """Search for entry name that matches the keyword. It is case-insensitive."""
    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            keyword = search_form.cleaned_data["keyword"]
            # if perfect match exists -> redirect
            match = get_match(keyword, util.list_entries())
            if match is not None:
                return HttpResponseRedirect(reverse("encyclopedia:wiki", kwargs={"title": match}))
            
            # if not -> list all possible results
            results = []
            for entry in util.list_entries():
                if keyword.lower() in entry.lower():
                    results.append(entry)
            return render(request, "encyclopedia/search.html", {
                "results": results,
                "keyword": keyword,
                "search_form": SearchForm(),
            })

    return HttpResponseRedirect(reverse("encyclopedia:index"))

def create(request):
    # receive post method
    if request.method == "POST":
        create_form = CreateForm(request.POST)
        if create_form.is_valid():
            title = create_form.cleaned_data["title"]
            content = create_form.cleaned_data["content"]
        else:
            messages.error(request, "Invalid form submission")
            return render(request, "encyclopedia/create.html", {
                "create_form": create_form,
                "search_form": SearchForm(),
            })
        
        # check if the page exists
        if get_match(title, util.list_entries()) is not None:
            messages.error(request, "Page already exists. Please edit the page or set a new page title.")
            return render(request, "encyclopedia/create.html", {
                "create_form": create_form,
                "search_form": SearchForm(),
            })
        
        # save the page entry into session
        util.save_entry(title, content)
        messages.success(request, "Create Success!")
        return HttpResponseRedirect(reverse("encyclopedia:wiki", kwargs={"title": title}))

    # when no submission, show a blank form
    return render(request, "encyclopedia/create.html", {
        "create_form": CreateForm(),
        "search_form": SearchForm(),
    })

def edit(request, title):
    if request.method == "GET":
        matched_title = get_match(title, util.list_entries())

        # when no matched title -> redirect to index
        if matched_title is None:
            messages.error(request, "The page you want to edit does not exist.")
            return index(request)

        content = util.get_entry(matched_title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "search_form": SearchForm(),
            "edit_form": EditForm(initial={'edit_content': content})
        })
    
    if request.method == "POST":
        edit_form = EditForm(request.POST)
        if edit_form.is_valid():
            # rewrite using save_entry
            content = edit_form.cleaned_data['edit_content']
            util.save_entry(title, content)
            messages.success(request, "Edit Success!")
            return HttpResponseRedirect(reverse("encyclopedia:wiki", kwargs={"title": title}))

# supplementary function
def get_match(key, choices):
    for choice in choices:
        if key.lower() == choice.lower():
            return choice
    return None

def is_subsequence(key, choice):
    if key.lower() in choice.lower():
        return True
    