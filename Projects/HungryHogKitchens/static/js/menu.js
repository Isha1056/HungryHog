$(document).ready(function() {
    $("body").on("click", ".Add", function () {
        $('.table_body').append(
            `
            <tr class="{{i.SNACK_ID}}">
                <td class="productID" style="display:none;"></td>
                <td colspan="2" class="name">
                    <div class="column-box">
                        <figure class="prod-thumb"><a href="#"><img
                                    src="{{ url_for('static', filename='/images/AddImage.svg') }}"
                                    width="150" height="150" alt="">
                                <h4 class="prod-title">
                                    <input type="text" class="input-name"
                                        value=""></input>
                                </h4>
                    </div>
                </td>
                <td class="price"><input type="text" class="input-price"
                        value=""></input></td>

                <td class="mealtype">
                    <select class="input-mealtype">
                        <option value="">Select Meal Type...</option>
                        {% for j in meals %}
                        <option value="{{j.Meal_ID}}">{{j.Meal_Type}} {{j.Meal_Timings}}</option>>
                        {% endfor %}
                    </select>
                </td>
                <td class="rating">0.0</td>
                <td class="save">
                    <div class="action_container">
                        <button class="success saveSnack">
                            <i class="fa fa-pencil-square-o"></i>
                        </button>
                    </div>
                </td>
                <td class="delete">
                    <div class="action_container">
                        <button class="danger removeSnack">
                            <i class="fa fa-close"></i>
                        </button>
                    </div>
                </td>
            </tr>
            `
        );
    });
});