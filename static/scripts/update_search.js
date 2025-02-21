function filterItems() {
    let query = document.getElementById("search_bar").value.toLowerCase();
    let books = document.getElementById("booksStorage").children;

    console.log(books);
    for (let book of books) {
        let text = book.querySelector(".card-text").textContent.toLowerCase();
        if (query) {
            if (text.includes(query)) {
                book.classList.remove("d-none");
            } else {
                book.classList.add("d-none");
            }
        } else {
            book.classList.remove("d-none");
        }
    }
}