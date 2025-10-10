let file = document.getElementById('file-upload');
let filename = document.getElementById('filename');
let profile_pic = document.getElementById('profile-pic');

function extract_filename(filename){
    output = filename.split('\\')[2];
    return output;
}

file.oninput = (e) => {
    filename.textContent = `Image uploaded : ${extract_filename(file.value)}`;
    profile_pic.src = URL.createObjectURL(file.files[0]);
}

file.onload = (e) => {
    URL.revokeObjectURL(profile_pic.src);
}