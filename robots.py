# Ajoutez cette route à votre application Flask
@app.route('/sitemap.xml')
def sitemap():
    base_url = request.host_url
    urls = [
        {'loc': base_url, 'changefreq': 'monthly', 'priority': '1.0'},
        {'loc': base_url + url_for('about'), 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': base_url + url_for('skills'), 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': base_url + url_for('experience'), 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': base_url + url_for('projects'), 'changefreq': 'monthly', 'priority': '0.9'},
        {'loc': base_url + url_for('contact'), 'changefreq': 'yearly', 'priority': '0.7'},
    ]
    
    sitemap_xml = render_template('sitemap.xml', urls=urls)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response