<?php

/* index/index.html */
class __TwigTemplate_5c989eaea289c5f0bd5fae76e8cd179bc81381c7ebcbb69fc0a3d33428377f3c extends Twig_Template
{
    public function __construct(Twig_Environment $env)
    {
        parent::__construct($env);

        $this->parent = false;

        $this->blocks = array(
        );
    }

    protected function doDisplay(array $context, array $blocks = array())
    {
        // line 1
        echo "前台
<a href=\"";
        // line 2
        echo twig_escape_filter($this->env, Tools_help::url("index/test", array("id" => "1", "name" => "codejm")), "html", null, true);
        echo "\" >测试</a>
";
    }

    public function getTemplateName()
    {
        return "index/index.html";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  22 => 2,  19 => 1,);
    }
}
