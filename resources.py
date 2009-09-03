selectall = """
<script language="JavaScript" type="text/javascript">
<!--
    function select()
    {
        el = document.getElementById('url');
        if (el.createTextRange) 
        {
            var oRange = el.createTextRange();
            oRange.moveStart("character", 0);
            oRange.moveEnd("character", el.value.length);
            oRange.select();
        }
        else if (el.setSelectionRange) 
        {
            el.setSelectionRange(0, el.value.length);
        }
        el.focus();
    }

    window.onload = select;
//-->
</script>
"""
