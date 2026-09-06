theorem research_os_add_zero : ∀ n : Nat, n + 0 = n := by
  intro n
  exact Nat.add_zero n

#print axioms research_os_add_zero
