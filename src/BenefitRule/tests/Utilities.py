# incompete
'''
issues:
	instruction stacking comparison
	how to show which instruction or expression doesnt match in test
'''
def compareTask(task_case, expected, other):
	for expected_instruction in expected.instruction_set.all():
		other_instruction = other.instruction_set.get(order=expected_instruction.order)
		task_case.assertEqual(other_instruction, expected_instruction)

		for expected_expression in expected_instruction.expression_set.all():
			other_expression = other_instruction.expression_set.get(order=expected_expression.order)
			task_case.assertEqual(other_expression, expected_expression)