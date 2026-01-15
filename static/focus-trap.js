// Simple reusable focus-trap utility
// Usage: const trap = createFocusTrap(container, { initialFocus, returnFocus, onDeactivate }); trap.activate(); trap.deactivate();
(function(window){
  function getFocusable(container){
    const selectors = ['a[href]','area[href]','input:not([disabled])','select:not([disabled])','textarea:not([disabled])','button:not([disabled])','iframe','object','embed','[tabindex]','[contenteditable]'];
    const nodes = Array.from(container.querySelectorAll(selectors.join(',')));
    return nodes.filter(el => el.tabIndex !== -1 && isVisible(el));
  }

  function isVisible(el){
    return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  }

  function createFocusTrap(container, options){
    options = options || {};
    let active = false;
    let previous = options.returnFocus || null;
    let onDeactivate = options.onDeactivate || function(){};

    function handleKey(e){
      if (!active) return;
      if (e.key === 'Escape'){
        e.preventDefault();
        onDeactivate();
        return;
      }
      if (e.key !== 'Tab') return;

      const focusable = getFocusable(container);
      if (focusable.length === 0){
        e.preventDefault();
        return;
      }

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const cur = document.activeElement;

      if (e.shiftKey){
        if (cur === first || !container.contains(cur)){
          e.preventDefault();
          last.focus();
        }
      } else {
        if (cur === last){
          e.preventDefault();
          first.focus();
        }
      }
    }

    return {
      activate(initialFocus){
        if (active) return;
        active = true;
        previous = previous || document.activeElement;
        document.addEventListener('keydown', handleKey);
        const focusTarget = initialFocus || container.querySelector('[data-initial-focus]') || getFocusable(container)[0] || container;
        try{ focusTarget.focus(); }catch(e){}
      },
      deactivate(){
        if (!active) return;
        active = false;
        document.removeEventListener('keydown', handleKey);
        try{ if (previous && typeof previous.focus === 'function') previous.focus(); }catch(e){}
        onDeactivate();
      }
    };
  }

  window.createFocusTrap = createFocusTrap;
})(window);
