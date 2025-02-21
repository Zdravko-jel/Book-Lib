document.getElementById("formFile").addEventListener("change", (event)=>{
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = (e)=>{
        const preview = document.getElementById("bookCover");
        preview.src = e.target.result;
    };

    if (file) {
        reader.readAsDataURL(file);
    }
});

function setValue(value) {
    document.getElementById("recommend").value = value;
    console.log("Recommend:", value); // For debugging
}

document.getElementById("editFormFile").addEventListener("change", (event)=>{
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = (e)=>{
        const preview = document.getElementById("currBookCover");
        preview.src = e.target.result;
    };

    if (file) {
        reader.readAsDataURL(file);
    }
});

function setValue(value) {
    document.getElementById("editRecommend").value = value;
    console.log("Recommend:", value); // For debugging
}