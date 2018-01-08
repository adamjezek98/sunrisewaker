HTML_BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="/jquery-3.2.1.min.js"></script>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <a href="/"/><h1>Alarms</h1></a>
    {body}
</body>
</html>
"""

ADD_BUTTON = """
<form action="/add">
    <input type="submit" value="Add alarm"/>
</form>
"""

TABLE = """<table border="1">
    <thead>
    <tr>
        <th>#</th>
        <th>Name</th>
        <th>Time</th>
        <th>Days</th>
        <th>Repeat</th>
        <th>Duration</th>
        <th>Will run at</th>
        <th>Edit</th>
    </tr>
    </thead>
    <tbody>    
        {tbody}    
    </tbody>
"""

TBODY = """ 
    <tr>
        <td>{id}</td>
        <td><a href="/edit/{id}">{name}</a></td>
        <td>{hour}:{minute}</td>
        <td>{active_days}</td>
        <td>{remaining_repeats}</td>
        <td>{duration}</td>
        <td>{start_at_string}</td>
        <td><form action="/edit/{id}">
            <input type="submit" value="Edit"/>
        </form></td>
    </tr>
"""

ALARM_EDIT = """
   <h2>Alarm {name}</h2>
    <form id="edit_form">
        <label>Name</label><input name="name" value="{name}"/><br/>
        <label>Time</label><input name="hour" value="{hour}"/>:<input name="minute" value="{minute}"/><br/>
        <label>Repeat</label><input name="repeat" value="{repeat}"/> -1 for infinite<br/>
        <label>Duration</label><input name="duration" value="{duration}"/>how many minutes to fully lit up<br/>
        <label>Days</label><br/>
        <label>Mon</label><input type="checkbox" name="mon" {mon}/><br/>
        <label>Tue</label><input type="checkbox" name="tue" {tue}/><br/>
        <label>Wed</label><input type="checkbox" name="wed" {wed}/><br/>
        <label>Thu</label><input type="checkbox" name="thu" {thu}/><br/>
        <label>Fri</label><input type="checkbox" name="fri" {fri}/><br/>
        <label>Sat</label><input type="checkbox" name="sat" {sat}/><br/>
        <label>Sun</label><input type="checkbox" name="sun" {sun}/><br/>
        <input name="id" value="{id}" hidden/>
        
        <button>Submit</button>
    </form>
    <label id="result"></label>
    """

FORM_JS = """
    <script>
        function submitForm() {
            $.ajax({
                type: "GET",
                url: "/set/",
                data: $('#edit_form').serialize(),
                success: function (result) {
                    $('#result').text(result);
                }
            });

        }
       
        $('#edit_form').submit(function () {
            submitForm();
            return false;
        });
    </script>
"""

REDIRECT = """<meta http-equiv="refresh" content="0; url={path}" />"""