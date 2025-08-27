rule ExampleRule {
    strings:
        $example_string = "example"
    condition:
        $example_string
}