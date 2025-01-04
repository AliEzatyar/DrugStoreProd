document.addEventListener("DOMContentLoaded", (e) => {


    function total() {
        var total = document.getElementById('id_total');
        var pricee = document.getElementById('id_price');
        var amount = document.getElementById('id_amount');
        total.value = Number(pricee.value) * Number(amount.value);
    }
    document.getElementById('id_price').addEventListener('keyup', total);
    document.getElementById('id_amount').addEventListener('keyup', total);

    // filling drugname selector
    var name_selector = document.getElementById('id_name')
    name_selector.innerHTML =
        `
            <option>انتخاب دارو</option>`
    name_selector.innerHTML += `
            {% for drug in drugs %}
                <option class="selector_option">
                    {{ drug }}
                </option>
            {% endfor %}
            `
    // filling company selector
    var company_selector = document.getElementById("id_company")
    name_selector.addEventListener('change', function (e) {
        company_selector.innerHTML = `
            <option>انتخاب شرکت</option>`
        const drugName = e.target.value
        const get_cmp_url = "{% url 'main:get_companies' %}"
        fetch(get_cmp_url + "?drug_name=" + drugName).
            then(response => response.json()).
            then(list => list.forEach(company => {
                function formatter(html, ...args) {
                    return html.reduce((acc, curr, i) => acc + args[i - 1] + curr);
                }
                company_selector.innerHTML += formatter`
                        <option>
                            ${company}
                        </option>
                        `
            })
            )
    })

    // new_drug button
    function new_drug() {
        document.querySelector(".name").innerHTML = `
            <label id="name_label">
                نام دارو:
            </label>
            <br>
            <input type="text" id="id_name" name="name">
            `
        document.querySelector(".company").innerHTML = `
            <label>
                شرکت دارو:
            </label>
            <input type="text" id="id_company" name="company">
            `
        document.getElementById("new_drug").remove()
        document.getElementById("img-preview").src = "{% static 'UsedPhoto/BedonAks.jpg' %}"
    }

    document.getElementById("new_drug").onclick = new_drug

    // making an image preview
    var img_preview = document.getElementById("img-preview")
    var file_input = document.getElementById("id_photo")

    // when drug exists before
    company_selector.addEventListener("change", function (e) {
        var new_drug = document.getElementById("new_drug")
        const company = e.target.value
        const drug_name = name_selector.value
        var url = "{% url "main: set_sld_photo" %}"
        fetch(url + "?name=" + drug_name
            + "&company=" + company).
            then(url => url.text()).
            then(photo_url => {
                img_preview.src = photo_url
            })
    })
    // when new drug is being added 
    file_input.addEventListener('change', function () {
        // Check if a file is selected
        if (file_input.files && file_input.files[0]) {
            // Create a FileReader object
            const reader = new FileReader();
            // Set a callback function to execute when the image is loaded
            reader.onload = function (e) {
                // Set the image source to the loaded data
                img_preview.src = e.target.result;
            };

            // Read the selected file as a URL
            reader.readAsDataURL(file_input.files[0]);
            x = reader.readAsDataURL(file_input.files[0])
        }
    });

    // showing errors
    {% if errors %}
    var company = document.getElementById('id_company')
    var name = document.getElementById('id_name')
    name.value = "{{ form.name.value }}"
    company.innerHTML = `
            <option>{{ form.company.value }}</option>`
        // sending a programmatic event to set the photo-- >
            { #company.dispatchEvent(new Event("change"))#} < active it if you want-- >
                name.dispatchEvent(new Event("change"))
    var date = document.getElementById('id_date')
    date.value = `{{ form.date.value }}`
    var photo = document.getElementById("id_photo")
    photo.src = "{% static 'UsedPhoto/BedonAks.jpg' %}"
    {% endif %}
})