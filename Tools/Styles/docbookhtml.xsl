<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE stylesheet [
<!ENTITY css SYSTEM "docbookhtml.css">
]>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
 <!-- xsl:import href="http://docbook.sourceforge.net/release/xsl/current/html/docbook.xsl"/ -->
 <xsl:import href="/usr/share/sgml/docbook/xsl-stylesheets/html/docbook.xsl"/>

 <xsl:param name="toc.max.depth">4711</xsl:param>
 <xsl:param name="toc.section.depth">4711</xsl:param>

 <xsl:template name="user.head.content">
  <style type="text/css">
   &css;
  </style>
 </xsl:template>
</xsl:stylesheet>
