document.getElementById("formFile").addEventListener("change", (event)=>{
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = (e)=>{
        const preview = document.getElementById("profilePreview");
        preview.src = e.target.result;
        preview.style.display = "block";
    };

    if (file) {
        reader.readAsDataURL(file);
    }
});
